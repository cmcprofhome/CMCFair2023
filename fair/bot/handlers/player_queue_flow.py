from logging import Logger

from telebot import TeleBot
from telebot.types import CallbackQuery

from fair.config import MessagesConfig, ButtonsConfig
from fair.db import DBAdapter, DBError
from fair.utils import dummy_true

from fair.bot import keyboards
from fair.bot.states import PlayerStates


# Player queue flow

# User is to come here after pressing the text button "New queue" in the main menu

# 1. If the user presses the button "New queue",
#    show the list of all available locations
#    as inline buttons with the name and a number of people in the corresponding queues.
#    1.1 If the user presses the button with the name of the location, add him to the queue of this location,
#        then he is to be redirected to the main menu.
# 2. If the user presses the button "My queue",
#    show the location where the user is in the queue, then he is to be redirected to the main menu.
# 3. If the user presses the button "Leave the queue", delete his queue, then he is to be redirected to the main menu.


def new_queue_location_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    location_id = call.data.split("#")[1]
    try:
        queue_entry_added = db_adapter.add_queue_entry_by_player_tg_id(call.from_user.id, location_id)
    except DBError as e:
        logger.error(f"{e}")
        bot.answer_callback_query(call.id, messages.unknown_error)
        return
    else:
        if queue_entry_added is False:
            logger.debug(f"Player {call.from_user.id} is already in the queue of location {location_id}")
            bot.send_message(call.message.chat.id, messages.queue_entry_already_exists_error)
            return
        else:
            logger.debug(f"Player {call.from_user.id} was added to the queue of location {location_id}")
            bot.set_state(call.message.from_user.id, PlayerStates.main_menu, call.message.chat.id)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboards.empty_inline())
            keyboard = keyboards.player_queue_menu(
                my_queue_btn=buttons.my_queue,
                leave_the_queue_btn=buttons.leave_queue,
                my_balance_btn=buttons.my_balance,
                transfer_money_btn=buttons.transfer_money,
                help_btn=buttons.help
            )
            bot.send_message(call.message.chat.id, messages.queue_entry_added, reply_markup=keyboard)


def new_queue_locations_page_handler(
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
        locations = db_adapter.get_all_active_locations(offset=page_idx * page_size, limit=page_size)
        locations_cnt = db_adapter.get_all_active_locations_count()
    except DBError as e:
        logger.error(f"{e}")
        bot.answer_callback_query(call.id, messages.unknown_error)
        return
    else:
        logger.debug(f"Player {call.from_user.id} is viewing page {page_idx} of locations list")
        keyboard = keyboards.collection_page(
            collection=[(f"{location.name} - {queue}", location.id) for location, queue in locations],
            collection_name="new_queue_locations",
            page_idx=page_idx,
            page_cnt=locations_cnt // page_size + 1,
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel
        )
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=keyboard)


def new_queue_location_cancel_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        logger: Logger,
        **kwargs):
    logger.debug(f"Player {call.from_user.id} cancelled choosing new queue location")
    bot.set_state(call.message.from_user.id, PlayerStates.main_menu, call.message.chat.id)
    bot.edit_message_text(
        text=messages.new_queue_location_cancelled,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboards.empty_inline()
    )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        new_queue_location_handler,
        func=dummy_true,
        cb_data_pagination="new_queue_locations",
        state=PlayerStates.choose_new_queue_location,
        pass_bot=True
    )
    bot.register_callback_query_handler(
        new_queue_locations_page_handler,
        func=dummy_true,
        cb_data_pagination="new_queue_locations_page",
        state=PlayerStates.choose_new_queue_location,
        pass_bot=True
    )
    bot.register_callback_query_handler(
        new_queue_location_cancel_handler,
        func=dummy_true,
        cb_data="new_queue_locations_cancel",
        state=PlayerStates.choose_new_queue_location,
        pass_bot=True
    )
