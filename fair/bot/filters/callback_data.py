from telebot.types import CallbackQuery
from telebot.custom_filters import AdvancedCustomFilter


class CallbackDataFilter(AdvancedCustomFilter):
    key = 'cb_data'

    def check(self, update: CallbackQuery, value: str):
        # exact match of the callback_data
        return update.data == value


class CallbackDataPaginationFilter(AdvancedCustomFilter):
    key = 'cb_data_pagination'

    def check(self, update: CallbackQuery, value: str):
        # check if callback_data starts with the value and contains a '#' sign right after it
        # useful for pagination, e.g. callback_data='paging_collection#number_of_the_page'
        return update.data.startswith(f'{value}#')
