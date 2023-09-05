import string
from logging import Logger

from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from fair.config import MessagesConfig, ButtonsConfig
from fair.db import DBAdapter, DBError
from fair.utils import dummy_true, ru_letters

from fair.bot import keyboards
from fair.bot.states import UnregisteredStates, PlayerStates


# Registration without a password

# User is to come here after a start command and pressing the inline button "Register as a player"
# with the "reg_player" callback_data

# 1 ask for a name, finish registration


def reg_player_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        **kwargs):
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=keyboards.empty_inline())
    bot.set_state(call.message.chat.id, UnregisteredStates.reg_player_name)
    bot.send_message(call.message.chat.id, messages.get_player_name)


def invalid_player_name_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        **kwargs):
    bot.send_message(message.chat.id, messages.invalid_player_name)


def player_name_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    try:
        name_available = db_adapter.check_player_name_availability(message.text)
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
    else:
        if name_available is False:
            logger.debug(f"Player name already exists: {message.text}")
            bot.send_message(message.chat.id, messages.player_name_already_taken)
            return
    try:
        player_added = db_adapter.add_player(message.from_user.id, message.text)  # add both User and Player
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
    else:
        if player_added is False:
            logger.error(
                f"Constraints violation while adding player:"
                f" {message.from_user.id}, {message.text}"
            )
            bot.delete_state(message.from_user.id, message.chat.id)
            bot.send_message(message.chat.id, messages.add_player_error)
        else:
            bot.set_state(message.chat.id, PlayerStates.main_menu)
            bot.send_message(
                message.chat.id,
                messages.player_registered,
                reply_markup=keyboards.player_main_menu(
                    buttons.new_queue,
                    buttons.my_balance,
                    buttons.transfer_money,
                    buttons.help
                )
            )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(reg_player_handler, func=dummy_true, cb_data="reg_player", pass_bot=True)
    bot.register_message_handler(
        player_name_handler,
        allowed_chars=string.ascii_letters + string.digits + ru_letters + " -_\"\'",
        state=UnregisteredStates.reg_player_name,
        pass_bot=True
    )
    bot.register_message_handler(
        invalid_player_name_handler,
        state=UnregisteredStates.reg_player_name,
        pass_bot=True
    )
