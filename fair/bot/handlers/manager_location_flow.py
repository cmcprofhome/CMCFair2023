from logging import Logger

from telebot import TeleBot
from telebot.types import CallbackQuery

from fair.config import MessagesConfig, ButtonsConfig
from fair.db import DBAdapter, DBError
from fair.utils import dummy_true

from fair.bot import keyboards
from fair.bot.states import ManagerStates


def choose_location_page_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    page_idx = int(call.data.split('#')[1])
    try:
        locations = db_adapter.get_all_locations(offset=page_idx * page_size, limit=page_size)
        locations_cnt = db_adapter.get_all_locations_count()
    except DBError as e:
        logger.error(e)
        bot.send_message(call.from_user.id, messages.unknown_error)
        return
    else:
        collection = list((f"{location.name} - {queue}", location.id) for location, queue in locations)
        keyboard = keyboards.collection_page(
            collection=collection,
            collection_name="choose_locations",
            page_idx=page_idx,
            page_cnt=round(locations_cnt / page_size + 0.5),
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel,
        )
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboard)


def choose_location_cancel_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        **kwargs):
    bot.set_state(call.from_user.id, ManagerStates.main_menu, call.message.chat.id)
    bot.edit_message_text(
        text=messages.choose_location_cancelled,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboards.empty_inline()
    )


def chosen_location_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    location_id = int(call.data.split('#')[1])
    try:
        location = db_adapter.get_location_by_id(location_id)
        manager_location_updated = False
        if location is not None:
            manager_location_updated = db_adapter.update_manager_location_by_tg_id(call.from_user.id, location_id)
    except DBError as e:
        logger.error(e)
        bot.send_message(call.from_user.id, messages.unknown_error)
        return
    else:
        if manager_location_updated is False:
            bot.send_message(call.from_user.id, messages.bad_location_error)
        else:
            bot.set_state(call.from_user.id, ManagerStates.main_menu, call.message.chat.id)
            bot.send_message(
                call.from_user.id,
                messages.location_updated,
                reply_markup=keyboards.manager_on_location_menu(
                    choose_location_btn=buttons.choose_location,
                    my_location_btn=buttons.my_location,
                    leave_the_location_btn=buttons.leave_location,
                    help_btn=buttons.help,
                )
            )
            bot.edit_message_text(
                text=messages.chosen_location.format(location.name),
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=keyboards.location_options(
                    my_location_queue_btn=buttons.my_location_queue,
                    pause_the_location_btn=buttons.my_location,
                )
            )


def my_location_queue_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    try:
        players = db_adapter.get_queue_by_manager_tg_id(call.from_user.id, offset=0, limit=page_size)
        players_cnt = db_adapter.get_queue_count_by_manager_tg_id(call.from_user.id)
    except DBError as e:
        logger.error(e)
        bot.send_message(call.from_user.id, messages.unknown_error)
        return
    else:
        collection = list((player.user.name, player.id) for player in players)
        keyboard = keyboards.collection_page(
            collection=collection,
            collection_name="my_location_queue",
            page_idx=0,
            page_cnt=round(players_cnt / page_size + 0.5),
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel,
        )
        bot.edit_message_text(
            text=messages.my_location_queue,
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=keyboard
        )


def my_location_queue_page_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        page_size: int,
        **kwargs):
    page_idx = int(call.data.split('#')[1])
    try:
        players = db_adapter.get_queue_by_manager_tg_id(call.from_user.id, offset=page_idx * page_size, limit=page_size)
        players_cnt = db_adapter.get_queue_count_by_manager_tg_id(call.from_user.id)
    except DBError as e:
        logger.error(e)
        bot.send_message(call.from_user.id, messages.unknown_error)
        return
    else:
        collection = list((player.user.name, player.id) for player in players)
        keyboard = keyboards.collection_page(
            collection=collection,
            collection_name="my_location_queue",
            page_idx=page_idx,
            page_cnt=round(players_cnt / page_size + 0.5),
            prev_page_btn=buttons.prev_page,
            next_page_btn=buttons.next_page,
            cancel_btn=buttons.cancel,
        )
        bot.edit_message_reply_markup(call.message.chat.id, call.message.id, reply_markup=keyboard)


def my_location_queue_cancel_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        **kwargs):
    bot.set_state(call.from_user.id, ManagerStates.main_menu, call.message.chat.id)
    bot.edit_message_text(
        text=messages.my_location_queue_cancelled,
        chat_id=call.message.chat.id,
        message_id=call.message.id,
        reply_markup=keyboards.location_options(
            my_location_queue_btn=buttons.my_location_queue,
            pause_the_location_btn=buttons.my_location,
        )
    )


def my_location_queue_chosen_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    try:
        location = db_adapter.get_location_by_manager_tg_id(call.from_user.id)
        shop = None
        if location is not None:
            shop = db_adapter.get_shop_by_location_id(location.id)
    except DBError as e:
        logger.error(e)
        bot.send_message(call.from_user.id, messages.unknown_error)
        return
    else:
        current_player_id = int(call.data.split('#')[1])
        bot.set_state(call.from_user.id, ManagerStates.location_player_chosen_options, call.message.chat.id)
        bot.add_data(call.from_user.id, call.message.chat.id, current_player_id=current_player_id)
        bot.edit_message_text(
            text=messages.location_player_chosen_options,
            chat_id=call.message.chat.id,
            message_id=call.message.id,
            reply_markup=keyboards.location_player_chosen_options(
                my_location_queue_btn=buttons.my_location_queue,
                reward_player_btn=buttons.reward_player if shop is not None else buttons.purchase,
                pause_the_location_btn=buttons.my_location
            )
        )


def pause_location_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    try:
        location_paused = db_adapter.update_location_by_manager_tg_id(call.from_user.id, is_active=False)
    except DBError as e:
        logger.error(e)
        bot.send_message(call.from_user.id, messages.unknown_error)
        return
    else:
        if location_paused is False:
            bot.send_message(call.from_user.id, messages.pause_location_error)
        else:
            bot.edit_message_text(
                text=messages.location_paused,
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=keyboards.location_paused_options(unpause_the_location_btn=buttons.unpause_location)
            )


def unpause_location_handler(
        call: CallbackQuery,
        bot: TeleBot,
        messages: MessagesConfig,
        buttons: ButtonsConfig,
        db_adapter: DBAdapter,
        logger: Logger,
        **kwargs):
    try:
        location_unpaused = db_adapter.update_location_by_manager_tg_id(call.from_user.id, is_active=True)
    except DBError as e:
        logger.error(e)
        bot.send_message(call.from_user.id, messages.unknown_error)
        return
    else:
        if location_unpaused is False:
            bot.send_message(call.from_user.id, messages.unpause_location_error)
        else:
            bot.edit_message_text(
                text=messages.location_unpaused,
                chat_id=call.message.chat.id,
                message_id=call.message.id,
                reply_markup=keyboards.location_options(
                    my_location_queue_btn=buttons.my_location_queue,
                    pause_the_location_btn=buttons.pause_location,
                )
            )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        choose_location_page_handler,
        func=dummy_true,
        cb_data_pagination="choose_locations_page",
        state=ManagerStates().state_list
    )
    bot.register_callback_query_handler(
        choose_location_cancel_handler,
        func=dummy_true,
        cb_data="choose_locations_cancel",
        state=ManagerStates().state_list
    )
    bot.register_callback_query_handler(
        chosen_location_handler,
        func=dummy_true,
        cb_data_pagination="choose_locations",
    )
    bot.register_callback_query_handler(
        my_location_queue_handler,
        func=dummy_true,
        cb_data="my_location_queue",
        state=ManagerStates().state_list
    )
    bot.register_callback_query_handler(
        my_location_queue_page_handler,
        func=dummy_true,
        cb_data_pagination="my_location_queue_page",
        state=ManagerStates().state_list
    )
    bot.register_callback_query_handler(
        my_location_queue_cancel_handler,
        func=dummy_true,
        cb_data="my_location_queue_cancel",
    )
    bot.register_callback_query_handler(
        my_location_queue_chosen_handler,
        func=dummy_true,
        cb_data_pagination="my_location_queue",
        state=ManagerStates().state_list
    )
    bot.register_callback_query_handler(
        pause_location_handler,
        func=dummy_true,
        cb_data="pause_location",
        state=ManagerStates().state_list
    )
    bot.register_callback_query_handler(
        unpause_location_handler,
        func=dummy_true,
        cb_data="unpause_location",
        state=ManagerStates().state_list
    )
