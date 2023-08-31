from telebot.handler_backends import State, StatesGroup

from fair.bot.states.storage import setup_state_storage


class UnregisteredStates(StatesGroup):
    reg_player_name = State()
    reg_manager_password = State()
    reg_manager_name = State()


class PlayerStates(StatesGroup):
    main_menu = State()
    new_queue_location = State()
    money_transfer_recipient = State()
    money_transfer_amount = State()


class ManagerStates(StatesGroup):
    main_menu = State()
    choose_location = State()
    my_location_queue = State()
    choose_from_queue = State()
    choose_reward_recipient = State()
    choose_reward_amount = State()
    choose_add_recipient = State()
    choose_add_amount = State()
    choose_subtract_recipient = State()
    choose_subtract_amount = State()
