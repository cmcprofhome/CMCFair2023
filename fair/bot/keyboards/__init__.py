from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


def reg_buttons(reg_player_btn: str, reg_manager_btn: str, help_btn: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text=reg_player_btn, callback_data="reg_player"))
    keyboard.row(InlineKeyboardButton(text=reg_manager_btn, callback_data="reg_manager"))
    keyboard.row(InlineKeyboardButton(text=help_btn, callback_data="help"))
    return keyboard


def player_main_menu(
        new_queue_btn: str,
        my_balance_btn: str,
        transfer_money_btn: str,
        help_btn: str) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton(text=new_queue_btn))
    keyboard.row(KeyboardButton(text=my_balance_btn))
    keyboard.row(KeyboardButton(text=transfer_money_btn))
    keyboard.row(KeyboardButton(text=help_btn))
    return keyboard


def player_queue_menu(
        my_queue_btn: str,
        leave_the_queue_btn: str,
        my_balance_btn: str,
        transfer_money_btn: str,
        help_btn: str) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton(text=my_queue_btn))
    keyboard.row(KeyboardButton(text=leave_the_queue_btn))
    keyboard.row(KeyboardButton(text=my_balance_btn))
    keyboard.row(KeyboardButton(text=transfer_money_btn))
    keyboard.row(KeyboardButton(text=help_btn))
    return keyboard


def collection_page(
        collection: list[tuple[str, int]],
        collection_name: str,
        page_idx: int,
        page_cnt: int,
        prev_page_btn: str,
        next_page_btn: str,
        cancel_btn: str) -> InlineKeyboardMarkup:
    # Collection name is used as a prefix for callback data.
    # Callback data format for collection entry: {collection_name}#{entry_id}
    # Callback data format for page control buttons: {collection_name}_page#{page_idx}
    # Callback data format for cancel button: {collection_name}_cancel
    # Each Callback data must be no longer than 64 bytes, choose collection name wisely.
    keyboard = InlineKeyboardMarkup()
    for entry in collection:
        keyboard.row(InlineKeyboardButton(text=collection[0], callback_data=f"{collection_name}#{entry[1]}"))
    control_btns = []
    if page_idx > 0:
        control_btns.append(
            InlineKeyboardButton(text=prev_page_btn, callback_data=f"{collection_name}_page#{page_idx - 1}")
        )
    if page_idx < page_cnt - 1:
        control_btns.append(
            InlineKeyboardButton(text=next_page_btn, callback_data=f"{collection_name}_page#{page_idx + 1}")
        )
    keyboard.row(*control_btns)
    keyboard.row(InlineKeyboardButton(text=cancel_btn, callback_data=f"{collection_name}_cancel"))
    return keyboard


def transfer_amount(cancel_btn: str) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    keyboard.row(KeyboardButton(text="10"), KeyboardButton(text="20"), KeyboardButton(text="30"),
                 KeyboardButton(text="50"), KeyboardButton(text="70"), KeyboardButton(text="100"))
    keyboard.row(KeyboardButton(text=cancel_btn))
    return keyboard


def manager_main_menu(
        list_all_players_btn: str,
        list_all_locations_btn: str,
        add_balance_btn: str,
        subtract_balance_btn: str,
        choose_location_btn: str,
        help_btn: str) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton(text=list_all_players_btn))
    keyboard.row(KeyboardButton(text=list_all_locations_btn))
    keyboard.row(KeyboardButton(text=add_balance_btn))
    keyboard.row(KeyboardButton(text=subtract_balance_btn))
    keyboard.row(KeyboardButton(text=choose_location_btn))
    keyboard.row(KeyboardButton(text=help_btn))
    return keyboard


def manager_on_location_menu(
        choose_location_btn: str,
        my_location_btn: str,
        leave_the_location_btn: str,
        help_btn: str) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton(text=choose_location_btn))
    keyboard.row(KeyboardButton(text=my_location_btn))
    keyboard.row(KeyboardButton(text=leave_the_location_btn))
    keyboard.row(KeyboardButton(text=help_btn))
    return keyboard


def location_options(my_location_queue_btn: str, pause_the_location_btn: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text=my_location_queue_btn, callback_data="my_location_queue"))
    keyboard.row(InlineKeyboardButton(text=pause_the_location_btn, callback_data="pause_the_location"))
    return keyboard


def location_player_chosen_options(
        my_location_queue_btn: str,
        reward_player_btn: str,
        pause_the_location_btn: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text=my_location_queue_btn, callback_data="my_location_queue"))
    keyboard.row(InlineKeyboardButton(text=reward_player_btn, callback_data="reward_player"))
    keyboard.row(InlineKeyboardButton(text=pause_the_location_btn, callback_data="pause_the_location"))
    return keyboard


def location_paused_options(unpause_the_location_btn: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton(text=unpause_the_location_btn, callback_data="unpause_the_location"))
    return keyboard


def reward_amount(cancel_btn: str) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    keyboard.row(KeyboardButton(text="0"), KeyboardButton(text="10"), KeyboardButton(text="30"),
                 KeyboardButton(text="50"), KeyboardButton(text="70"), KeyboardButton(text="100"))
    keyboard.row(KeyboardButton(text=cancel_btn))
    return keyboard


def purchase_amount(cancel_btn: str) -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    keyboard.row(KeyboardButton(text="50"), KeyboardButton(text="100"), KeyboardButton(text="200"),
                 KeyboardButton(text="300"), KeyboardButton(text="400"), KeyboardButton(text="500"))
    keyboard.row(KeyboardButton(text=cancel_btn))
    return keyboard
