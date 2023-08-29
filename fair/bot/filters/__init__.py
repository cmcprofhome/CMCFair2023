from telebot import TeleBot
from telebot.custom_filters import StateFilter


from fair.bot.filters.callback_data import CallbackDataFilter, CallbackDataPaginationFilter
from fair.bot.filters.text import TextEqualsFilter


def add_custom_filters(bot: TeleBot):
    # add any custom filters here
    bot.add_custom_filter(StateFilter(bot))

    bot.add_custom_filter(TextEqualsFilter())

    bot.add_custom_filter(CallbackDataFilter())
    bot.add_custom_filter(CallbackDataPaginationFilter())
