import logging
from typing import Optional, Callable

from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fair.db.exceptions import DBError
from fair.db.models import (
    TelegramAccount,
    User, Player, Manager,
    ManagersBlacklistRecord,
    Location, Shop,
    QueueEntry, FinishedLocation
)
from fair.db.operations import (
    role, telegram_account,
    user, player, manager,
    managers_blacklist_record,
    location, shop,
    queue_entry, finished_location,
    transfer_record, reward_record, purchase_record
)


class DBAdapter:
    def __init__(self, session_maker: sessionmaker, logger: logging.Logger):
        self.logger = logger
        self.session_maker = session_maker

    def _session_wrapper(self, method: Callable, *args, **kwargs):
        try:
            with self.session_maker() as session:
                return method(session, *args, **kwargs)
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while {method.__name__}: {e}")

    def _commit_session_wrapper(self, method: Callable, *args, **kwargs):
        try:
            with self.session_maker.begin() as session:
                return method(session, *args, **kwargs)
        except IntegrityError as e:
            self.logger.debug(e)
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while {method.__name__}: {e}")

    def add_role(self, name: str) -> bool:
        return self._commit_session_wrapper(role.add, name)

    def delete_role_by_name(self, name: str) -> bool:
        return self._commit_session_wrapper(role.delete_by_name, name)

    def add_telegram_account(self, tg_user_id: int, tg_chat_id: int, tg_username: Optional[str] = None) -> bool:
        return self._commit_session_wrapper(telegram_account.add, tg_user_id, tg_chat_id, tg_username)

    def get_telegram_account(self, tg_user_id: int) -> Optional[TelegramAccount]:
        return self._session_wrapper(telegram_account.get, tg_user_id)

    def update_telegram_account_username(self, tg_user_id: int, tg_username: str) -> bool:
        return self._commit_session_wrapper(telegram_account.add, tg_user_id, tg_username)

    def add_user(self, role_name: str, tg_user_id: int) -> bool:
        return self._commit_session_wrapper(user.add, role_name, tg_user_id)

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return self._session_wrapper(user.get_by_id, user_id)

    def get_user_by_tg_id(self, tg_user_id: int) -> Optional[User]:
        return self._session_wrapper(user.get_by_tg_id, tg_user_id)

    def check_player_name_availability(self, name: str) -> bool:
        return self._session_wrapper(player.check_name_availability, name)

    def add_player(self, tg_user_id: int, name: str) -> bool:
        return self._commit_session_wrapper(player.add, tg_user_id, name)

    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        return self._session_wrapper(player.get_by_id, player_id)

    def get_player_by_tg_id(self, tg_user_id: int) -> Optional[Player]:
        return self._session_wrapper(player.get_by_tg_id, tg_user_id)

    def get_all_players(self, offset: int, limit: int) -> list[Player]:
        return self._session_wrapper(player.get_all, offset, limit)

    def get_all_players_count(self) -> int:
        return self._session_wrapper(player.get_all_count)

    def update_player_balance_by_id(self, player_id: int, amount: int) -> bool:
        return self._commit_session_wrapper(player.update_balance_by_id, player_id, amount)

    def update_player_balance_by_tg_id(self, tg_user_id: int, amount: int) -> bool:
        return self._commit_session_wrapper(player.update_balance_by_tg_id, tg_user_id, amount)

    def transfer_by_player_id(self, from_player_id: int, to_player_id: int, amount: int) -> bool:
        transferred = self._commit_session_wrapper(player.transfer_by_id, from_player_id, to_player_id, amount)
        if transferred:
            try:
                self.add_transfer_record(from_player_id, to_player_id, amount)
            except DBError:
                pass  # suppress error
        return transferred

    def transfer_by_player_tg_id(self, from_user_tg_id: int, to_user_tg_id: int, amount: int) -> bool:
        transferred = self._commit_session_wrapper(player.transfer_by_tg_id, from_user_tg_id, to_user_tg_id, amount)
        if transferred:
            try:
                self.add_transfer_record(from_user_tg_id, to_user_tg_id, amount)
            except DBError:
                pass  # suppress error
        return transferred

    def check_manager_name_availability(self, name: str) -> bool:
        return self._session_wrapper(manager.check_name_availability, name)

    def add_manager(self, tg_user_id: int, name: str) -> bool:
        return self._commit_session_wrapper(manager.add, tg_user_id, name)

    def get_manager_by_id(self, manager_id: int) -> Optional[Manager]:
        return self._session_wrapper(manager.get_by_id, manager_id)

    def get_manager_by_tg_id(self, tg_user_id: int) -> Optional[Manager]:
        return self._session_wrapper(manager.get_by_tg_id, tg_user_id)

    def update_manager_location_by_id(self, manager_id: int, new_location_id: Optional[int] = None) -> bool:
        return self._commit_session_wrapper(manager.update_location_by_id, manager_id, new_location_id)

    def update_manager_location_by_tg_id(self, tg_user_id: int, new_location_id: Optional[int] = None) -> bool:
        return self._commit_session_wrapper(manager.update_location_by_tg_id, tg_user_id, new_location_id)

    def add_managers_blacklist_record(self, tg_user_id: int) -> bool:
        return self._commit_session_wrapper(managers_blacklist_record.add, tg_user_id)

    def get_managers_blacklist_record(self, tg_user_id: int) -> Optional[ManagersBlacklistRecord]:
        return self._session_wrapper(managers_blacklist_record.get_by_tg_id, tg_user_id)

    def delete_managers_blacklist_record(self, tg_user_id: int) -> bool:
        return self._commit_session_wrapper(managers_blacklist_record.delete_by_tg_id, tg_user_id)

    def add_location(self, name: str, max_reward: int, is_onetime: bool) -> bool:
        return self._commit_session_wrapper(location.add, name, max_reward, is_onetime)

    def get_location_by_id(self, location_id: int) -> Optional[Location]:
        return self._session_wrapper(location.get_by_id, location_id)

    def get_location_by_manager_id(self, manager_id: int) -> Optional[Location]:
        return self._session_wrapper(location.get_by_manager_id, manager_id)

    def get_location_by_manager_tg_id(self, tg_user_id: int) -> Optional[Location]:
        return self._session_wrapper(location.get_by_manager_tg_id, tg_user_id)

    def get_all_locations(self, offset: int, limit: int) -> list[tuple[Location, int]]:
        return self._session_wrapper(location.get_all, offset, limit)

    def get_all_locations_count(self) -> int:
        return self._session_wrapper(location.get_all_count)

    def get_all_active_locations(self, offset: int, limit: int) -> list[tuple[Location, int]]:
        return self._session_wrapper(location.get_all_active, offset, limit)

    def get_all_active_locations_count(self) -> int:
        return self._session_wrapper(location.get_all_active_count)

    def update_location_by_id(self, location_id: int, is_active: bool) -> bool:
        return self._commit_session_wrapper(location.update_by_id, location_id, is_active)

    def update_location_by_manager_id(self, manager_id: int, is_active: bool) -> bool:
        return self._commit_session_wrapper(location.update_by_manager_id, manager_id, is_active)

    def update_location_by_manager_tg_id(self, tg_user_id: int, is_active: bool) -> bool:
        return self._commit_session_wrapper(location.update_by_manager_tg_id, tg_user_id, is_active)

    def add_shop(self, location_id: int, name: str) -> bool:
        return self._commit_session_wrapper(shop.add, location_id, name)

    def get_shop_by_id(self, shop_id: int) -> Optional[Shop]:
        return self._session_wrapper(shop.get_by_id, shop_id)

    def get_shop_by_location_id(self, location_id: int) -> Optional[Shop]:
        return self._session_wrapper(shop.get_by_location_id, location_id)

    def add_queue_entry_by_player_id(self, player_id: int, location_id: int) -> bool:
        return self._commit_session_wrapper(queue_entry.add_by_player_id, player_id, location_id)

    def add_queue_entry_by_player_tg_id(self, tg_user_id: int, location_id: int) -> bool:
        return self._commit_session_wrapper(queue_entry.add_by_player_tg_id, tg_user_id, location_id)

    def get_queue_entry_by_player_id(self, player_id: int) -> Optional[QueueEntry]:
        return self._session_wrapper(queue_entry.get_by_player_id, player_id)

    def get_queue_entry_by_player_tg_id(self, tg_user_id: int) -> Optional[QueueEntry]:
        return self._session_wrapper(queue_entry.get_by_player_tg_id, tg_user_id)

    def get_queue_by_location_id(self, location_id: int, offset: int, limit: int) -> list[Player]:
        return self._session_wrapper(queue_entry.get_by_location_id, location_id, offset, limit)

    def get_queue_by_manager_id(self, manager_id: int, offset: int, limit: int) -> list[Player]:
        return self._session_wrapper(queue_entry.get_by_manager_id, manager_id, offset, limit)

    def get_queue_by_manager_tg_id(self, tg_user_id: int, offset: int, limit: int) -> list[Player]:
        return self._session_wrapper(queue_entry.get_by_manager_tg_id, tg_user_id, offset, limit)

    def get_queue_count_by_location_id(self, location_id: int) -> int:
        return self._session_wrapper(queue_entry.get_count_by_location_id, location_id)

    def get_queue_count_by_manager_id(self, manager_id: int) -> int:
        return self._session_wrapper(queue_entry.get_count_by_manager_id, manager_id)

    def get_queue_count_by_manager_tg_id(self, tg_user_id: int) -> int:
        return self._session_wrapper(queue_entry.get_count_by_manager_tg_id, tg_user_id)

    def delete_queue_entry_by_player_id(self, player_id: int) -> bool:
        return self._commit_session_wrapper(queue_entry.delete_by_player_id, player_id)

    def delete_queue_entry_by_player_tg_id(self, tg_user_id: int) -> bool:
        return self._commit_session_wrapper(queue_entry.delete_by_player_tg_id, tg_user_id)

    def add_finished_location_by_player_id(self, player_id: int, location_id: int) -> bool:
        return self._commit_session_wrapper(finished_location.add_by_player_id, player_id, location_id)

    def add_finished_location_by_player_tg_id(self, tg_user_id: int, location_id: int) -> bool:
        return self._commit_session_wrapper(finished_location.add_by_player_tg_id, tg_user_id, location_id)

    def get_finished_locations_by_player_id(self, player_id: int) -> list[FinishedLocation]:
        return self._session_wrapper(finished_location.get_by_player_id, player_id)

    def get_finished_locations_by_player_tg_id(self, tg_user_id: int) -> list[FinishedLocation]:
        return self._session_wrapper(finished_location.get_by_player_tg_id, tg_user_id)

    def add_transfer_record(self, from_player_id: int, to_player_id: int, amount: int) -> bool:
        return self._commit_session_wrapper(transfer_record.add, from_player_id, to_player_id, amount)

    def add_reward_record(self, player_id: int, location_id: int, manager_id: int, amount: int) -> bool:
        return self._commit_session_wrapper(reward_record.add, player_id, location_id, manager_id, amount)

    def add_purchase_record(self, player_id: int, shop_id: int, manager_id: int, amount: int) -> bool:
        return self._commit_session_wrapper(purchase_record.add, player_id, shop_id, manager_id, amount)

    def purchase_by_player_id(self, player_id: int, manager_id: int, amount: int) -> bool:
        balance_updated = self.update_player_balance_by_id(player_id, -amount)
        if balance_updated:
            try:
                _location = self.get_location_by_manager_id(manager_id)
                if _location:
                    _shop = self.get_shop_by_location_id(_location.id)
                    if _shop:
                        self.add_purchase_record(player_id, _shop.id, manager_id, amount)
            except DBError:
                pass  # suppress error
        return balance_updated

    def reward_by_player_id(self, player_id: int, manager_id: int, amount: int) -> bool:
        balance_updated = self.update_player_balance_by_id(player_id, amount)
        if balance_updated:
            try:
                _location = self.get_location_by_manager_id(manager_id)
                if _location:
                    self.add_reward_record(player_id, _location.id, manager_id, amount)
            except DBError:
                pass  # suppress error
        return balance_updated
