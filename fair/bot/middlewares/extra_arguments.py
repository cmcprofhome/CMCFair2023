import logging

from telebot.types import Update
from telebot.handler_backends import BaseMiddleware

from fair.config import MessagesConfig, ButtonsConfig
from fair.db import DBAdapter


class ExtraArgumentsMiddleware(BaseMiddleware):
    def __init__(self, db_adapter: DBAdapter, messages: MessagesConfig, buttons: ButtonsConfig, logger: logging.Logger):
        super().__init__()
        self.db_adapter = db_adapter
        self.messages = messages
        self.buttons = buttons
        self.logger = logger
        self.update_types = ['message', 'callback_query']

    def pre_process(self, message: Update, data: dict):
        # passing extra arguments to handlers
        data['db_adapter'] = self.db_adapter
        data['messages'] = self.messages
        data['buttons'] = self.buttons
        data['logger'] = self.logger

    def post_process(self, message: Update, data: dict, exception: BaseException):
        pass
