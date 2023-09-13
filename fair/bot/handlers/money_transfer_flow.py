from logging import Logger

from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from fair.config import MessagesConfig, ButtonsConfig
from fair.db import DBAdapter, DBError
from fair.utils import dummy_true

from fair.bot import keyboards
from fair.bot.states import PlayerStates


# Money transfers from player to player

# User is to come here after pressing the text button "Money transfer"

# 1. Show a list of players with pages (10 players per page) to be a recipient
# 2. Ask for an amount with a few template values as inline buttons (e.g. 10, 50, 100, 500, 1000)
# 3. Finish the transfer


def money_transfer_recipient_page_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    page_idx = int(call.data.split("#")[1])
    try:
        players = db_adapter.get_all_players(offset=page_idx * page_size, limit=page_size)
        players_cnt = db_adapter.get_all_players_count()
    except DBError as e:
        logger.error(e)
        bot.answer_callback_query(call.id, text=messages.unknown_error)
        return
    else:
        logger.debug(f"Player {call.from_user.id} is choosing a recipient for money transfer on page {page_idx}")
        keyboard = keyboards.collection_page(
            collection=[(player.name, player.id) for player in players],
            collection_name="transfer_recipients",
            page_idx=page_idx,
            page_cnt=round(players_cnt // page_size + 0.5),
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel
        )
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboard)


def money_transfer_recipient_cancel_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        logger: Logger,
        **kwargs):
    logger.debug(f"Player {call.from_user.id} cancelled choosing a recipient for money transfer")
    bot.set_state(call.from_user.id, PlayerStates.main_menu, call.message.chat.id)
    bot.edit_message_text(
        text=messages.money_transfer_recipient_cancelled,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboards.empty_inline()
    )


def money_transfer_recipient_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        logger: Logger,
        **kwargs):
    recipient_player_id = call.data.split("#")[1]
    logger.debug(f"Player {call.from_user.id} chose a recipient {recipient_player_id} for money transfer")
    bot.add_data(call.from_user.id, call.message.chat.id, recipient_player_id=recipient_player_id)
    bot.set_state(call.from_user.id, PlayerStates.choose_money_transfer_amount, call.message.chat.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboards.empty_inline())
    bot.send_message(
        chat_id=call.message.chat.id,
        text=messages.choose_money_transfer_amount,
        reply_markup=keyboards.transfer_amount(buttons.cancel)
    )


def money_transfer_amount_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        recipient_player_id = data.get("recipient_player_id")
    if recipient_player_id is None:
        logger.debug(f"Player {message.from_user.id} is trying to transfer money without choosing a recipient")
        bot.send_message(
            chat_id=message.chat.id,
            text=messages.money_transfer_recipient_not_chosen_error,
            reply_markup=keyboards.empty_inline()
        )
        bot.set_state(message.from_user.id, PlayerStates.main_menu, message.chat.id)
        return
    else:
        try:
            player = db_adapter.get_player_by_tg_id(message.from_user.id)
            queue_entry = db_adapter.get_queue_entry_by_player_id(player.id)
            money_transferred = False
            if player is not None:
                money_transferred = db_adapter.transfer_by_player_id(player.id, recipient_player_id, int(message.text))
        except DBError as e:
            logger.error(e)
            bot.send_message(chat_id=message.chat.id, text=messages.unknown_error)
            return
        else:
            if money_transferred is False:
                logger.debug(f"Player {message.from_user.id} is trying to transfer money with invalid amount")
                bot.send_message(chat_id=message.chat.id, text=messages.money_transfer_amount_invalid_error)
                return
            else:
                logger.debug(f"Player {message.from_user.id} transferred money to player {recipient_player_id}")
                if queue_entry is None:
                    keyboard = keyboards.player_main_menu(
                        new_queue_btn=buttons.new_queue,
                        my_balance_btn=buttons.my_balance,
                        transfer_money_btn=buttons.transfer_money,
                        help_btn=buttons.help
                    )
                else:
                    keyboard = keyboards.player_queue_menu(
                        my_queue_btn=buttons.my_queue,
                        leave_the_queue_btn=buttons.leave_queue,
                        my_balance_btn=buttons.my_balance,
                        transfer_money_btn=buttons.transfer_money,
                        help_btn=buttons.help
                    )
                bot.set_state(message.from_user.id, PlayerStates.main_menu, message.chat.id)
                bot.send_message(
                    chat_id=message.chat.id,
                    text=messages.money_transfer_success,
                    reply_markup=keyboard
                )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        money_transfer_recipient_page_handler,
        func=dummy_true,
        cb_data_pagination="transfer_recipients_page",
        state=PlayerStates.choose_money_transfer_recipient,
        pass_bot=True
    )
    bot.register_callback_query_handler(
        money_transfer_recipient_cancel_handler,
        func=dummy_true,
        cb_data="transfer_recipient_cancel",
        state=PlayerStates.choose_money_transfer_recipient,
        pass_bot=True
    )
    bot.register_callback_query_handler(
        money_transfer_recipient_handler,
        func=dummy_true,
        cb_data_pagination="transfer_recipients",
        state=PlayerStates.choose_money_transfer_recipient,
        pass_bot=True
    )
    bot.register_message_handler(
        money_transfer_amount_handler,
        is_digit=True,
        state=PlayerStates.choose_money_transfer_amount,
        pass_bot=True
    )
