from telebot import TeleBot

from fair.config import ButtonsConfig

from fair.bot.handlers import (
    player_permanent_menu
)


def register_handlers(bot: TeleBot, buttons: ButtonsConfig):
    # register all handlers here
    player_permanent_menu.register_handlers(bot, buttons)
