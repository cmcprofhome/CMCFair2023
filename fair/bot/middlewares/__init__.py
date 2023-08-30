import logging

from telebot import TeleBot

from fair.db import DBAdapter
from fair.config import MessagesConfig, ButtonsConfig

from fair.bot.middlewares.message_antiflood import MessageAntiFloodMiddleware
from fair.bot.middlewares.callback_query_antiflood import CallbackQueryAntiFloodMiddleware
from fair.bot.middlewares.extra_arguments import ExtraArgumentsMiddleware


def setup_middlewares(
        bot: TeleBot,
        timeout_message: str,
        timeout: float,
        db_adapter: DBAdapter,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        logger: logging.Logger):
    # setup all middlewares here
    bot.setup_middleware(MessageAntiFloodMiddleware(bot, timeout_message, timeout))
    bot.setup_middleware(CallbackQueryAntiFloodMiddleware(bot, timeout_message, timeout))
    bot.setup_middleware(ExtraArgumentsMiddleware(db_adapter, messages, buttons, logger))
    pass
