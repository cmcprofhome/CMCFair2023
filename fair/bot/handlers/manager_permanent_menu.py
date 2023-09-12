from logging import Logger

from telebot import TeleBot
from telebot.types import Message, CallbackQuery

from fair.config import MessagesConfig, ButtonsConfig
from fair.db import DBAdapter, DBError

from fair.bot import keyboards
from fair.bot.states import ManagerStates


# Manager's permanent menu with text buttons

# 1. Help
# 2. Choose location
# 3. My location
# 4.1 Reward a player
# 4.2 Purchase
# 5. List all players with pages (10 players per page)
# 6. List all locations with pages (10 locations per page), sorted by the number of players in a queue
# 7. Add money to player's balance
# 8. Subtract money from player's balance


def list_all_players_handler(
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
        players_cnt = db_adapter.get_all_players_count()
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        collection = list((player.user.name, player.id) for player in players)
        keyboard = keyboards.collection_page(
            collection=collection,
            collection_name="players",
            page_idx=0,
            page_cnt=round(players_cnt / page_size + 0.5),
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel
        )
        bot.send_message(message.chat.id, messages.all_players, reply_markup=keyboard)


def all_players_page_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    page_idx = int(call.data.split("#")[1])
    try:
        players = db_adapter.get_all_players(offset=page_idx * page_size, limit=page_size)
        players_cnt = db_adapter.get_all_players_count()
    except DBError as e:
        logger.error(e)
        bot.send_message(call.message.chat.id, messages.unknown_error)
        return
    else:
        collection = list((player.user.name, player.id) for player in players)
        keyboard = keyboards.collection_page(
            collection=collection,
            collection_name="players",
            page_idx=page_idx,
            page_cnt=round(players_cnt / page_size + 0.5),
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel
        )
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=keyboard
        )


def all_players_cancel_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        **kwargs):
    bot.edit_message_text(
        text=messages.all_players_cancelled,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboards.empty_inline()
    )


def list_all_locations_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    try:
        locations = db_adapter.get_all_locations(offset=0, limit=page_size)
        locations_cnt = db_adapter.get_all_locations_count()
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        collection = list((f"{location.name} - {queue}", location.id) for location, queue in locations)
        keyboard = keyboards.collection_page(
            collection=collection,
            collection_name="locations",
            page_idx=0,
            page_cnt=round(locations_cnt / page_size + 0.5),
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel
        )
        bot.send_message(message.chat.id, messages.all_locations, reply_markup=keyboard)


def all_locations_page_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    page_idx = int(call.data.split("#")[1])
    try:
        locations = db_adapter.get_all_locations(offset=page_idx * page_size, limit=page_size)
        locations_cnt = db_adapter.get_all_locations_count()
    except DBError as e:
        logger.error(e)
        bot.send_message(call.message.chat.id, messages.unknown_error)
        return
    else:
        collection = list((f"{location.name} - {queue}", location.id) for location, queue in locations)
        keyboard = keyboards.collection_page(
            collection=collection,
            collection_name="locations",
            page_idx=page_idx,
            page_cnt=round(locations_cnt / page_size + 0.5),
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel
        )
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=keyboard
        )


def all_locations_cancel_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        **kwargs):
    bot.edit_message_text(
        text=messages.all_locations_cancelled,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboards.empty_inline()
    )


def create_recipients_keyboard(db_adapter: DBAdapter, buttons: ButtonsConfig, collection_name: str, page_size: int):
    players = db_adapter.get_all_players(offset=0, limit=page_size)
    players_cnt = db_adapter.get_all_players_count()
    collection = list((player.user.name, player.id) for player in players)
    keyboard = keyboards.collection_page(
        collection=collection,
        collection_name=collection_name,
        page_idx=0,
        page_cnt=round(players_cnt / page_size + 0.5),
        prev_page_btn=buttons.prev_page,
        next_page_btn=buttons.next_page,
        cancel_btn=buttons.cancel
    )
    return keyboard


def add_balance_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    try:
        keyboard = create_recipients_keyboard(db_adapter, buttons, "add_balance_recipients", page_size)
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        bot.set_state(message.from_user.id, ManagerStates.choose_add_recipient, message.chat.id)
        bot.send_message(message.chat.id, messages.choose_add_balance_recipient, reply_markup=keyboard)


def subtract_balance_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    try:
        keyboard = create_recipients_keyboard(db_adapter, buttons, "subtract_balance_recipients", page_size)
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        bot.set_state(message.from_user.id, ManagerStates.choose_subtract_recipient, message.chat.id)
        bot.send_message(message.chat.id, messages.choose_subtract_balance_recipient, reply_markup=keyboard)


def reward_player_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    try:
        keyboard = create_recipients_keyboard(db_adapter, buttons, "reward_recipients", page_size)
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        bot.set_state(message.from_user.id, ManagerStates.choose_reward_recipient, message.chat.id)
        bot.send_message(message.chat.id, messages.choose_reward_recipient, reply_markup=keyboard)


def purchase_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    try:
        keyboard = create_recipients_keyboard(db_adapter, buttons, "purchase_recipients", page_size)
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        bot.set_state(message.from_user.id, ManagerStates.choose_purchase_recipient, message.chat.id)
        bot.send_message(message.chat.id, messages.choose_purchase_recipient, reply_markup=keyboard)


def recipient_page_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    collection_name = call.data.split("#")[0]
    page_idx = int(call.data.split("#")[1])
    try:
        players = db_adapter.get_all_players(offset=page_idx * page_size, limit=page_size)
        players_cnt = db_adapter.get_all_players_count()
    except DBError as e:
        logger.error(e)
        bot.send_message(call.message.chat.id, messages.unknown_error)
        return
    else:
        collection = list((player.user.name, player.id) for player in players)
        keyboard = keyboards.collection_page(
            collection=collection,
            collection_name=collection_name,
            page_idx=page_idx,
            page_cnt=round(players_cnt / page_size + 0.5),
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel
        )
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=keyboard
        )


def recipient_cancel_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        **kwargs):
    msg = messages.unknown_error
    bot.set_state(call.from_user.id, ManagerStates.main_menu)
    if "add_balance_recipients" in call.data:
        msg = messages.add_balance_cancelled
    elif "subtract_balance_recipients" in call.data:
        msg = messages.subtract_balance_cancelled
    elif "reward_recipients" in call.data:
        msg = messages.reward_cancelled
    elif "purchase_recipients" in call.data:
        msg = messages.purchase_cancelled
    bot.edit_message_text(
        text=msg,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboards.empty_inline()
    )


def recipient_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        **kwargs):
    recipient_player_id = int(call.data.split("#")[1])
    bot.add_data(call.from_user.id, call.message.chat.id, recipient_player_id=recipient_player_id)
    msg = messages.unknown_error
    if "add_balance_recipients" in call.data:
        msg = messages.choose_add_balance_amount
        bot.set_state(call.from_user.id, ManagerStates.choose_add_amount)
    elif "subtract_balance_recipients" in call.data:
        msg = messages.choose_subtract_balance_amount
        bot.set_state(call.from_user.id, ManagerStates.choose_subtract_amount)
    elif "reward_recipients" in call.data:
        msg = messages.choose_reward_amount
        bot.set_state(call.from_user.id, ManagerStates.choose_reward_amount)
    elif "purchase_recipients" in call.data:
        msg = messages.choose_purchase_amount
        bot.set_state(call.from_user.id, ManagerStates.choose_purchase_amount)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboards.empty_inline())
    bot.send_message(chat_id=call.message.chat.id, text=msg)


def choose_location_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    try:
        locations = db_adapter.get_all_locations(offset=0, limit=page_size)
        locations_cnt = db_adapter.get_all_locations_count()
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        collection = list((f"{location.name} - {queue}", location.id) for location, queue in locations)
        keyboard = keyboards.collection_page(
            collection=collection,
            collection_name="choose_locations",
            page_idx=0,
            page_cnt=round(locations_cnt / page_size + 0.5),
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel
        )
        bot.set_state(message.from_user.id, ManagerStates.choose_location, message.chat.id)
        bot.send_message(message.chat.id, messages.choose_location, reply_markup=keyboard)


def my_location_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    try:
        location = db_adapter.get_location_by_manager_tg_id(message.from_user.id)
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        if location is None:
            bot.send_message(message.chat.id, messages.manager_not_on_location_error)
        else:
            bot.send_message(
                message.chat.id,
                messages.manager_my_location.format(location.name, len(location.queue)),
                reply_markup=keyboards.location_options(
                    my_location_queue_btn=buttons.my_location_queue,
                    pause_the_location_btn=buttons.pause_location
                )
            )


def leave_location_handler(
        message: Message,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    try:
        manager_location_updated = db_adapter.update_manager_location_by_tg_id(message.from_user.id, None)
    except DBError as e:
        logger.error(e)
        bot.send_message(message.chat.id, messages.unknown_error)
        return
    else:
        if manager_location_updated is False:
            bot.send_message(message.chat.id, messages.manager_not_on_location_error)
        else:
            bot.send_message(
                message.chat.id,
                messages.manager_left_location,
                reply_markup=keyboards.manager_main_menu(
                    list_all_players_btn=buttons.list_all_players,
                    list_all_locations_btn=buttons.list_all_locations,
                    add_balance_btn=buttons.add_balance,
                    subtract_balance_btn=buttons.subtract_balance,
                    choose_location_btn=buttons.choose_location,
                    help_btn=buttons.help
                )
            )


def register_handlers(bot: TeleBot, buttons: ButtonsConfig):
    bot.register_message_handler(
        list_all_players_handler,
        text_equals=buttons.list_all_players,
        state=ManagerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        list_all_locations_handler,
        text_equals=buttons.list_all_locations,
        state=ManagerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        add_balance_handler,
        text_equals=buttons.add_balance,
        state=ManagerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        subtract_balance_handler,
        text_equals=buttons.subtract_balance,
        state=ManagerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        reward_player_handler,
        text_equals=buttons.reward_player,
        state=ManagerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        purchase_handler,
        text_equals=buttons.purchase,
        state=ManagerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        choose_location_handler,
        text_equals=buttons.choose_location,
        state=ManagerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        my_location_handler,
        text_equals=buttons.my_location,
        state=ManagerStates().state_list,
        pass_bot=True
    )
    bot.register_message_handler(
        leave_location_handler,
        text_equals=buttons.leave_location,
        state=ManagerStates().state_list,
        pass_bot=True
    )
