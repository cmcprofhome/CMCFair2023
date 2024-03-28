from logging import Logger

from telebot import TeleBot
from telebot.types import Message, CallbackQuery
from telebot.util import extract_arguments

from fair.config import MessagesConfig, ButtonsConfig
from fair.db import DBAdapter, DBError
from fair.utils import dummy_true

from fair.bot import keyboards
from fair.bot.states import ManagerStates


# Admins permanent menu with text buttons

# 1. Help
# 5. Add new location
# 6. Remove location


def reset_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    bot.delete_state(message.from_user.id, message.chat.id)
    try:
        db_adapter.delete_managers_blacklist_record(message.from_user.id)
        db_adapter.delete_queue_entry_by_player_tg_id(message.from_user.id)
        db_adapter.update_manager_location_by_tg_id(message.from_user.id, None)
        db_adapter.delete_player_by_tg_id(message.from_user.id)
        db_adapter.delete_manager_by_tg_id(message.from_user.id)
        db_adapter.delete_user_by_tg_id(message.from_user.id)
        db_adapter.session.commit()
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        db_adapter.session.rollback()
        return
    else:
        bot.send_message(message.chat.id, "Press /start to start again", reply_markup=keyboards.remove_reply())


def set_manager_password_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    password = extract_arguments(message.text)
    if password:
        bot.add_data(bot.user.id, bot.user.id, manager_password=password)
        logger.debug(f"{message.from_user.id} set manager password: {password}")
        bot.send_message(message.chat.id, messages.manager_password_set)
    else:
        bot.reset_data(bot.user.id, bot.user.id)
        logger.debug(f"{message.from_user.id} reset manager password")
        bot.send_message(message.chat.id, messages.manager_password_reset)


def add_location_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    name, max_reward, is_onetime = extract_arguments(message.text).split()
    if name and max_reward and max_reward.isdigit() and is_onetime in ["True", "False", "true", "false", "1", "0"]:
        try:
            db_adapter.add_location(name, int(max_reward), bool(is_onetime))
            db_adapter.session.commit()
            logger.debug(f"{message.from_user.id} added location: "
                         f"{name}, max_reward: {max_reward}, is_onetime: {is_onetime}")
        except DBError as e:
            logger.error(e)
            bot.send_message(message.chat.id, messages.unknown_error)
            db_adapter.session.rollback()
            return
        else:
            bot.send_message(message.chat.id, messages.location_added)
    else:
        bot.send_message(message.chat.id, messages.invalid_add_location_args)


def register_handlers(bot: TeleBot):
    bot.register_message_handler(reset_handler, commands=['reset'], pass_bot=True)
    bot.register_message_handler(
        set_manager_password_handler,
        commands=['set_manager_password'],
        is_owner=True,
        pass_bot=True
    )
    bot.register_message_handler(add_location_handler, commands=['add_location'], is_owner=True, pass_bot=True)
