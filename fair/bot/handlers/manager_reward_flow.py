from logging import Logger

from telebot import TeleBot
from telebot.types import Message

from fair.bot import keyboards
from fair.config import MessagesConfig, ButtonsConfig
from fair.db import DBAdapter, DBError

from fair.bot.states import ManagerStates


# Reward user for completing a task at the location, only for managers

# 1. Show the list of players in the queue with pages (10 players per page)
# 2. Choose a player from the list
# 3. Ask for a reward amount with pre-defined templates (e.g. 10, 20, 30, 50, 100), custom amounts are questionable


def reward_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        current_player_id = data.get("current_player_id", None)
        try:
            player = db_adapter.get_player_by_id(current_player_id)
            manager = db_adapter.get_manager_by_tg_id(message.from_user.id)
        except DBError as e:
            logger.error(e)
            bot.send_message(message.chat.id, messages.unknown_error)
            return
        else:
            keyboard = keyboards.manager_on_location_menu(
                choose_location_btn=buttons.my_location,
                my_location_btn=buttons.my_location,
                leave_the_location_btn=buttons.leave_location,
                help_btn=buttons.help
            )
            if manager is not None:
                if player is not None:
                    amount = int(message.text)
                    try:
                        balance_status = db_adapter.reward_by_player_id(current_player_id, manager.id, amount)
                        db_adapter.session.commit()
                    except DBError as e:
                        logger.error(e)
                        bot.send_message(message.chat.id, messages.unknown_error)
                        db_adapter.session.rollback()
                        return
                    else:
                        if balance_status:
                            bot.send_message(message.chat.id, messages.reward_successful, reply_markup=keyboard)
                            bot.set_state(message.from_user.id, ManagerStates.main_menu, message.chat.id)
                        else:
                            bot.send_message(message.chat.id, messages.bad_player_balance_error, reply_markup=keyboard)
                else:
                    bot.send_message(message.chat.id, messages.bad_chosen_player_error, reply_markup=keyboard)
            else:
                bot.send_message(message.chat.id, messages.bad_manager_error, reply_markup=keyboard)


def register_handlers(bot: TeleBot):
    bot.register_message_handler(
        reward_handler,
        state=ManagerStates.choose_purchase_amount,
        pass_bot=True,
        is_digit=True
    )
