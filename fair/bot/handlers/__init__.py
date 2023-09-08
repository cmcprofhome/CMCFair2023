from telebot import TeleBot

from fair.config import ButtonsConfig

from fair.bot.handlers import (
    money_transfer_flow
)


def register_handlers(bot: TeleBot, buttons: ButtonsConfig):
    # register all handlers here
    money_transfer_flow.register_handlers(bot)
