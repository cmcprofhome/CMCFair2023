from logging import Logger

from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from fair.config import MessagesConfig, ButtonsConfig
from fair.db import DBAdapter, DBError
from fair.utils import dummy_true

from fair.bot import keyboards
from fair.bot.states import UnregisteredStates, PlayerStates, ManagerStates


# Basic commands

# 1. start - send a help message, send a welcome message with inline registration buttons
# 2. help - send a help message


def start_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    bot.set_state(message.from_user.id, UnregisteredStates.started, message.chat.id)
    try:
        tg_account = db_adapter.get_telegram_account(message.from_user.id)
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        if tg_account is None:
            try:
                tg_account_added = db_adapter.add_telegram_account(
                    message.from_user.id,
                    message.chat.id,
                    message.from_user.username
                )
                db_adapter.session.commit()
            except DBError as e:
                logger.error(e)
                bot.send_message(message.chat.id, messages.unknown_error)
                db_adapter.session.rollback()
                return
            else:
                if tg_account_added is False:
                    logger.error(
                        f'Constraints violation while adding telegram account:'
                        f' {message.from_user.id}, {message.chat.id}, {message.from_user.username}'
                    )
                    bot.send_message(message.chat.id, messages.add_tg_account_error)
                    return
                else:
                    logger.debug(
                        f'Telegram account added:'
                        f' {message.from_user.id}, {message.chat.id}, {message.from_user.username}'
                    )
        bot.send_message(
            message.chat.id, messages.welcome,
            reply_markup=keyboards.reg_buttons(buttons.reg_player, buttons.reg_manager, buttons.help)
        )


def unregistered_help_button_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        **kwargs):
    bot.send_message(
        call.message.chat.id, messages.unregistered_help,
        reply_markup=keyboards.reg_buttons(buttons.reg_player, buttons.reg_manager, buttons.help)
    )


def unregistered_help_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        **kwargs):
    bot.send_message(
        message.chat.id, messages.unregistered_help,
        reply_markup=keyboards.reg_buttons(buttons.reg_player, buttons.reg_manager, buttons.help)
    )


def player_help_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        **kwargs):
    bot.send_message(message.chat.id, messages.player_help)


def manager_help_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        **kwargs):
    bot.send_message(message.chat.id, messages.manager_help)


def owner_help_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        **kwargs):
    bot.send_message(message.chat.id, messages.owner_help)


def register_handlers(bot: TeleBot, buttons: ButtonsConfig):
    bot.register_message_handler(start_handler, commands=['start'], state=[None], pass_bot=True)
    bot.register_callback_query_handler(
        unregistered_help_button_handler,
        func=dummy_true,
        cb_data="help",
        state=UnregisteredStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        unregistered_help_handler,
        commands=['help'],
        state=UnregisteredStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        player_help_handler,
        commands=['help'],
        state=PlayerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        player_help_handler,
        text_equals=buttons.help,
        state=PlayerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        manager_help_handler,
        commands=['help'],
        state=ManagerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        manager_help_handler,
        text_equals=buttons.help,
        state=ManagerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(owner_help_handler, commands=['help'], is_owner=True, pass_bot=True)
    bot.register_message_handler(owner_help_handler, text_equals=buttons.help, is_owner=True, pass_bot=True)
