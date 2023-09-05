from telebot import TeleBot

from fair.config import ButtonsConfig

from fair.bot.handlers import (
    player_registration_flow,
)


def register_handlers(bot: TeleBot, buttons: ButtonsConfig):
    player_registration_flow.register_handlers(bot)
