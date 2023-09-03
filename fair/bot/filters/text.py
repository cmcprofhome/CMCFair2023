from telebot.types import Message
from telebot.custom_filters import AdvancedCustomFilter


class TextEqualsFilter(AdvancedCustomFilter):
    key = 'text_equals'

    def check(self, update: Message, value: str):
        # exact match of the text
        return update.text == value
