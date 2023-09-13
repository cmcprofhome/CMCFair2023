from telebot.handler_backends import State, StatesGroup

from fair.bot.states.storage import setup_state_storage


class UnregisteredStates(StatesGroup):
    reg_player_name = State()
    reg_manager_password = State()
    reg_manager_name = State()


class PlayerStates(StatesGroup):
    main_menu = State()
    choose_new_queue_location = State()
    choose_money_transfer_recipient = State()
    choose_money_transfer_amount = State()


class ManagerStates(StatesGroup):
    main_menu = State()
    location_options = State()
    location_player_chosen_options = State()
    location_paused_options = State()
    choose_location = State()
    choose_from_my_location_queue = State()
    choose_reward_recipient = State()
    choose_reward_amount = State()
    choose_purchase_recipient = State()
    choose_purchase_amount = State()
    choose_add_recipient = State()
    choose_add_amount = State()
    choose_subtract_recipient = State()
    choose_subtract_amount = State()
