import string
from logging import Logger

from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from fair.config import MessagesConfig, ButtonsConfig
from fair.db import DBAdapter, DBError
from fair.utils import dummy_true, ru_letters

from fair.bot import keyboards
from fair.bot.states import UnregisteredStates, ManagerStates


# Registration with manager password

# User is to come here after a start command and pressing the inline button "Register as a manager"
# with the "reg_manager" callback_data

# 1. ask for password with 3 retries
#    1.1 if password is correct, proceed
#    1.2 if password is incorrect, put into a managers blacklist
# 2 ask for a name, finish registration


def reg_manager_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    try:
        manager_blacklist_record = db_adapter.get_managers_blacklist_record(call.from_user.id)
    except DBError as e:
        logger.error(e)
        bot.send_message(call.message.chat.id, messages.unknown_error)
        return
    else:
        if manager_blacklist_record is not None:
            logger.debug(f"{call.from_user.id} trying to register as a manager when in the blacklist")
            bot.send_message(call.message.chat.id, messages.manager_registration_forbidden)
        else:
            with bot.retrieve_data(bot.user.id, bot.user.id) as data:
                manager_password = data.get("manager_password", None)
            if manager_password is None:
                logger.debug(f"{call.from_user.id} trying to register as a manager when password is not set")
                bot.send_message(call.message.chat.id, messages.manager_registration_disabled)
            else:
                bot.edit_message_reply_markup(
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=keyboards.empty_inline()
                )
                bot.set_state(call.from_user.id, UnregisteredStates.reg_manager_password, call.message.chat.id)
                bot.send_message(call.message.chat.id, messages.get_manager_password)


def manager_password_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        password_retries = data.get("password_retries", 0)
    bot.delete_state(message.from_user.id, message.chat.id)
    with bot.retrieve_data(bot.user.id, bot.user.id) as data:
        manager_password = data.get("manager_password", None)
    if manager_password is None:
        logger.debug(f"{message.from_user.id} trying to register as a manager when password is not set")
        bot.send_message(message.chat.id, messages.manager_registration_disabled)
    else:
        if message.text == manager_password:
            logger.debug(f"{message.from_user.id} trying to register as a manager, correct password")
            bot.set_state(message.from_user.id, UnregisteredStates.reg_manager_name, message.chat.id)
            bot.send_message(message.chat.id, messages.get_manager_name)
        else:
            if password_retries == 2:
                try:
                    db_adapter.add_managers_blacklist_record(message.from_user.id)
                except DBError as e:
                    logger.error(e)
                    bot.send_message(message.chat.id, messages.unknown_error)
                    return
                else:
                    logger.debug(f"{message.from_user.id} trying to register as a manager is now in blacklist")
                    bot.send_message(message.chat.id, messages.manager_registration_forbidden)
            else:
                logger.debug(f"{message.from_user.id} trying to register as a manager, incorrect password")
                bot.set_state(message.from_user.id, UnregisteredStates.reg_manager_password, message.chat.id)
                bot.add_data(message.from_user.id, message.chat.id, password_retries=password_retries + 1)
                bot.send_message(message.chat.id, messages.get_manager_password)


def invalid_manager_name_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        **kwargs):
    bot.send_message(message.chat.id, messages.invalid_manager_name)


def manager_name_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    try:
        name_available = db_adapter.check_manager_name_availability(message.text)
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        if name_available is False:
            logger.debug(f"Manager name already exists: {message.text}")
            bot.send_message(message.chat.id, messages.manager_name_already_taken)
            return
    try:
        user_added = db_adapter.add_user("manager", message.from_user.id)  # add User
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        if user_added is False:
            logger.error(
                f"Constraints violation while adding user:"
                f" {message.from_user.id}, {message.text}"
            )
            bot.send_message(message.chat.id, messages.add_user_error)
            return
        else:
            logger.debug(f"User added: {message.from_user.id}, {message.text}")
    try:
        manager_added = db_adapter.add_manager(message.from_user.id, message.text)  # add Manager
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        if manager_added is False:
            logger.error(
                f"Constraints violation while adding manager:"
                f" {message.from_user.id}, {message.text}"
            )
            bot.delete_state(message.from_user.id, message.chat.id)
            bot.send_message(message.chat.id, messages.add_manager_error)
        else:
            logger.debug(f"Manager added: {message.from_user.id}, {message.text}")
            bot.set_state(message.chat.id, ManagerStates.main_menu)
            bot.send_message(
                message.chat.id,
                messages.manager_registered,
                reply_markup=keyboards.manager_main_menu(
                    buttons.list_all_players,
                    buttons.list_all_locations,
                    buttons.add_balance,
                    buttons.subtract_balance,
                    buttons.choose_location,
                    buttons.help
                )
            )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(reg_manager_handler, func=dummy_true, cb_data="reg_manager", pass_bot=True)
    bot.register_message_handler(
        manager_password_handler,
        state=UnregisteredStates.reg_manager_password,
        pass_bot=True
    )
    bot.register_message_handler(
        manager_name_handler,
        allowed_chars=string.ascii_letters + ru_letters + " -",
        state=UnregisteredStates.reg_manager_name,
        pass_bot=True
    )
    bot.register_message_handler(
        invalid_manager_name_handler,
        state=UnregisteredStates.reg_manager_name,
        pass_bot=True
    )
