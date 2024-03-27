import logging

from telebot.handler_backends import BaseMiddleware

from fair.config import MessagesConfig, ButtonsConfig
from fair.db import sessionmaker, DBAdapter


class ExtraArgumentsMiddleware(BaseMiddleware):
    def __init__(
            self,
            db_session_maker: sessionmaker,
            db_logger: logging.Logger,
            messages: MessagesConfig,
            buttons: ButtonsConfig,
            logger: logging.Logger,
            page_size: int):
        super().__init__()
        self.db_session_maker = db_session_maker
        self.db_logger = db_logger
        self.messages = messages
        self.buttons = buttons
        self.logger = logger
        self.page_size = page_size
        self.update_types = ['message', 'callback_query']

    def pre_process(self, message, data: dict):
        # passing extra arguments to handlers
        data['db_adapter'] = DBAdapter(self.db_session_maker(), self.db_logger)
        data['messages'] = self.messages
        data['buttons'] = self.buttons
        data['logger'] = self.logger
        data['page_size'] = self.page_size

    def post_process(self, message, data: dict, exception: BaseException):
        data['db_adapter'].session.close()
