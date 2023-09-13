from telebot.types import Message
from telebot.custom_filters import AdvancedCustomFilter


class TextEqualsFilter(AdvancedCustomFilter):
    key = 'text_equals'

    def check(self, update: Message, value: str):
        # exact match of the text
        return update.text == value


class AllowedCharsFilter(AdvancedCustomFilter):
    key = 'allowed_chars'

    def check(self, update: Message, value: str):
        # check if all characters in the text are from the value
        return all(ch in value for ch in update.text)
