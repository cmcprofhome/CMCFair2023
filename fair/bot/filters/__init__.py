from telebot import TeleBot
from telebot.custom_filters import StateFilter


def add_custom_filters(bot: TeleBot):
    # add any custom filters here
    bot.add_custom_filter(StateFilter(bot))
