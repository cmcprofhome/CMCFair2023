from telebot import TeleBot
from telebot.custom_filters import StateFilter


from fair.bot.filters.callback_data import CallbackDataFilter, CallbackDataPaginationFilter
from fair.bot.filters.text import TextEqualsFilter, AllowedCharsFilter
from fair.bot.filters.roles import IsOwnerFilter


def add_custom_filters(bot: TeleBot, owner_tg_id: int):
    # add any custom filters here
    bot.add_custom_filter(StateFilter(bot))

    bot.add_custom_filter(TextEqualsFilter())
    bot.add_custom_filter(AllowedCharsFilter())

    bot.add_custom_filter(CallbackDataFilter())
    bot.add_custom_filter(CallbackDataPaginationFilter())

    bot.add_custom_filter(IsOwnerFilter(owner_tg_id))
