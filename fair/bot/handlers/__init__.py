from telebot import TeleBot

from fair.config import ButtonsConfig

from fair.bot.handlers import (
    basic_commands_flow,
    player_registration_flow,
    manager_registration_flow,
    player_permanent_menu,
    player_queue_flow,
    money_transfer_flow,
    manager_permanent_menu,
)


def register_handlers(bot: TeleBot, buttons: ButtonsConfig):
    # register all handlers here
    basic_commands_flow.register_handlers(bot, buttons)
    player_registration_flow.register_handlers(bot)
    manager_registration_flow.register_handlers(bot)
    player_permanent_menu.register_handlers(bot, buttons)
    player_queue_flow.register_handlers(bot)
    money_transfer_flow.register_handlers(bot)
    manager_permanent_menu.register_handlers(bot, buttons)
