import string
from logging import Logger

from telebot import TeleBot
from telebot.types import Message

from fair.config import MessagesConfig
from fair.db import DBAdapter, DBError

from fair.bot.states import ManagerStates


# Cashier flow

# 1. Get the list of players in the queue with pages (10 players per page)
# 2. Choose the player to interact with
# 3. Finish the purchase (inline button), notify the player


def purchase_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        current_player_id = data.get("current_player_id", None)                                         # TODO: add current_player_id to state payload
        try:
            player = db_adapter.get_player_by_id(current_player_id)
        except DBError as e:
            logger.error(e)
            bot.send_message(call.message.chat.id, messages.unknown_error)
            return
        else:
            if player is not None:
                amount = int(message.text)
                if player.balance - amount > 0:
                    db_adapter.update_player_balance_by_id(current_player_id, -int(message.text))
                    bot.send_message(message.chat.id, messages.purchase_amount)                         # TODO: add purchase_amount message
                    bot.set_state(message.from_user.id, ManagerStates.main_menu, message.chat.id)
                else:
                    bot.send_message(message.chat.id, messages.bad_player_balance)                      # TODO: add bad_player_balance message


def register_handlers(bot: TeleBot):
    bot.register_message_handler(
        purchase_handler,
        state=ManagerStates.choose_purchase_amount,
        pass_bot=True,
        is_digit=True
    )