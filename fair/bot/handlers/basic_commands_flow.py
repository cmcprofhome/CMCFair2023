from telebot import TeleBot
from telebot.types import Message

from fair.bot import keyboards
from fair.bot.states import UnregisteredStates, PlayerStates, ManagerStates
from fair.config import MessagesConfig, ButtonsConfig


# Basic commands

# 1. start - send a help message, send a welcome message with inline registration buttons
# 2. help - send a help message


def start_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        **kwargs):
    bot.send_message(
        message.chat.id, messages.welcome,
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
    bot.register_message_handler(start_handler, commands=['start'], state=[None])
    bot.register_message_handler(unregistered_help_handler, commands=['help'], state=UnregisteredStates().state_list)
    bot.register_message_handler(
        unregistered_help_handler,
        text_equals=buttons.help,
        state=UnregisteredStates().state_list
    )
    bot.register_message_handler(player_help_handler, commands=['help'], state=PlayerStates().state_list)
    bot.register_message_handler(
        player_help_handler,
        text_equals=buttons.help,
        state=PlayerStates().state_list
    )
    bot.register_message_handler(manager_help_handler, commands=['help'], state=ManagerStates().state_list)
    bot.register_message_handler(
        manager_help_handler,
        text_equals=buttons.help,
        state=ManagerStates().state_list
    )
    bot.register_message_handler(owner_help_handler, commands=['help'], is_owner=True)
    bot.register_message_handler(owner_help_handler, text_equals=buttons.help, is_owner=True)
