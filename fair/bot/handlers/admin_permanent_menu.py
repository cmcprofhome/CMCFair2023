from logging import Logger

from telebot import TeleBot
from telebot.types import Message, CallbackQuery

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


def register_handlers(bot: TeleBot):
    bot.register_message_handler(reset_handler, commands=['reset'], pass_bot=True)
