from logging import Logger

from telebot import TeleBot
from telebot.types import Message

from fair.config import MessagesConfig, ButtonsConfig
from fair.db import DBAdapter, DBError

from fair.bot import keyboards
from fair.bot.states import PlayerStates


# Player's permanent menu with text buttons

# 1. New queue
# 2. My queue
# 3. Leave the queue
# 4. My balance
# 5. Transfer money


def my_balance_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    try:
        player = db_adapter.get_player_by_tg_id(message.from_user.id)
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        if player is None:
            logger.debug(f"Player with tg_id {message.from_user.id} not found!")
            bot.send_message(message.chat.id, messages.player_not_found_error)
        else:
            bot.send_message(message.chat.id, messages.player_balance.format(player.balance))


def transfer_money_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    try:
        players = db_adapter.get_all_players(offset=0, limit=page_size)
        players_cnt = db_adapter.get_players_count()
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        logger.debug(f"Player with tg_id {message.from_user.id} initiated money transfer")
        keyboard = keyboards.collection_page(
            collection=[(player.user.name, player.id) for player in players],
            collection_name='transfer_recipients',
            page_idx=0,
            page_cnt=round(players_cnt / page_size + 0.5),
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel,
        )
        bot.set_state(message.from_user.id, PlayerStates.choose_money_transfer_recipient, message.chat.id)
        bot.send_message(message.chat.id, messages.choose_money_transfer_recipient, reply_markup=keyboard)


def new_queue_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    try:
        locations = db_adapter.get_all_active_locations(offset=0, limit=page_size)
        locations_cnt = db_adapter.get_active_locations_count()
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        logger.debug(f"Player with tg_id {message.from_user.id} initiated new queue")
        keyboard = keyboards.collection_page(
            collection=[(location.name, location.id) for location in locations],
            collection_name='new_queue_locations',
            page_idx=0,
            page_cnt=round(locations_cnt / page_size + 0.5),
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel,
        )
        bot.set_state(message.from_user.id, PlayerStates.choose_new_queue_location, message.chat.id)
        bot.send_message(message.chat.id, messages.choose_new_queue_location, reply_markup=keyboard)


def my_queue_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    try:
        queue_entry = db_adapter.get_queue_entry_by_player_tg_id(message.from_user.id)
        location = None
        if queue_entry is not None:
            location = db_adapter.get_location_by_id(queue_entry.location_id)
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        if location is None:
            logger.debug("Player is not in queue, when trying to get his queue info")
            bot.send_message(message.chat.id, messages.player_not_in_queue_error)
        else:
            bot.send_message(
                message.chat.id,
                messages.player_queue_location.format(location.name, len(location.queues))
            )


def leave_queue_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    try:
        queue_entry_deleted = db_adapter.delete_queue_entry_by_player_tg_id(message.from_user.id)
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        if queue_entry_deleted is False:
            logger.debug("Player is not in queue, when trying to leave it")
            bot.send_message(message.chat.id, messages.player_not_in_queue_error)
        else:
            logger.debug(f"Player with tg_id {message.from_user.id} left queue")
            bot.send_message(message.chat.id, messages.player_left_queue)


def register_handlers(bot: TeleBot, buttons: ButtonsConfig):
    bot.register_message_handler(
        my_balance_handler,
        text_equals=buttons.my_balance,
        state=PlayerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        transfer_money_handler,
        text_equals=buttons.transfer_money,
        state=PlayerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        new_queue_handler,
        text_equals=buttons.new_queue,
        state=PlayerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        my_queue_handler,
        text_equals=buttons.my_queue,
        state=PlayerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        leave_queue_handler,
        text_equals=buttons.leave_queue,
        state=PlayerStates().state_list,
        pass_bot=True
    )
