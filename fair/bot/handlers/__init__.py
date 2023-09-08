from telebot import TeleBot

from fair.config import ButtonsConfig

from fair.bot.handlers import (
    player_queue_flow
)


def register_handlers(bot: TeleBot, buttons: ButtonsConfig):
    # register all handlers here
    player_queue_flow.register_handlers(bot)
