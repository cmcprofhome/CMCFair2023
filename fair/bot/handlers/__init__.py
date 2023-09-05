from telebot import TeleBot

from fair.config import ButtonsConfig

from fair.bot.handlers import (
    manager_registration_flow
)


def register_handlers(bot: TeleBot, buttons: ButtonsConfig):
    # register all handlers here
    manager_registration_flow.register_handlers(bot)
    pass
