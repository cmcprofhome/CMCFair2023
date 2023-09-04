from telebot import TeleBot

from fair.config import ButtonsConfig

from fair.bot.handlers import (
    basic_commands_flow
)


def register_handlers(bot: TeleBot, buttons: ButtonsConfig):
    basic_commands_flow.register_handlers(bot, buttons)
