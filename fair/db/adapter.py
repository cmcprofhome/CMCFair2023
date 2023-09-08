import logging
from typing import Optional

from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, insert, update, delete, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fair.db.exceptions import DBError
from fair.db.models import (
    Role, TelegramAccount,
    User, Player, Manager,
    ManagersBlacklistRecord,
    Location, Shop,
    QueueEntry, FinishedLocation,
    TransferRecord, RewardRecord, PurchaseRecord
)


class DBAdapter:
    def __init__(self, session_maker: sessionmaker, logger: logging.Logger):
        self.logger = logger
        self.session_maker = session_maker

    def add_telegram_account(self, tg_user_id: int, tg_chat_id: int, tg_username: Optional[str] = None) -> bool:
        try:
            with self.session_maker.begin() as session:
                session.execute(
                    insert(TelegramAccount)
                    .values(tg_user_id=tg_user_id, tg_chat_id=tg_chat_id, tg_username=tg_username)
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding telegram account to database: {e}")

    def get_telegram_account(self, tg_user_id: int) -> Optional[TelegramAccount]:
        try:
            with self.session_maker() as session:
                account = session.execute(
                    select(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).first()
            return account if account is None else account[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting telegram account from database: {e}")

    def update_telegram_account_username(self, tg_user_id: int, tg_username: str) -> bool:
        try:
            with self.session_maker.begin() as session:
                result = session.execute(
                    update(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                    .values(tg_username=tg_username)
                ).rowcount
            return result != 0
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while updating telegram account username in database: {e}")

    def add_user(self, role_name: str, tg_user_id: int, user_name: str) -> bool:
        try:
            with self.session_maker.begin() as session:
                role_id = session.execute(
                    select(Role.id)
                    .where(Role.name == role_name)
                ).first()
                if role_id is None:
                    raise DBError(f"Role with name '{role_name}' does not exist!")
                else:
                    role_id = role_id[0]
                tg_account_id = session.execute(
                    select(TelegramAccount.id)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).first()
                if tg_account_id is None:
                    raise DBError(f"Telegram account with tg_user_id '{tg_user_id}' does not exist!")
                else:
                    tg_account_id = tg_account_id[0]
                session.execute(
                    insert(User)
                    .values(role_id=role_id, name=user_name, tg_account_id=tg_account_id)
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding user to database: {e}")

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        try:
            with self.session_maker() as session:
                user = session.execute(
                    select(User)
                    .where(User.id == user_id)
                ).first()
            return user if user is None else user[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting user from database: {e}")

    def get_user_by_tg_id(self, tg_user_id: int) -> Optional[User]:
        try:
            with self.session_maker() as session:
                user = session.execute(
                    select(User)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).first()
            return user if user is None else user[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting user from database: {e}")

    def check_player_name_availability(self, name: str) -> bool:
        try:
            with self.session_maker() as session:
                result = session.execute(
                    select(User)
                    .where(User.name == name)
                ).first()
            return result is None
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while checking player name availability in database: {e}")

    def add_player(self, tg_user_id: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                user_id = (
                    select(User.id)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).scalar_subquery()
                session.execute(
                    insert(Player)
                    .values(user_id=user_id)
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding player to database: {e}")

    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        try:
            with self.session_maker() as session:
                player = session.execute(
                    select(Player)
                    .where(Player.id == player_id)
                ).first()
            return player if player is None else player[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting player from database: {e}")

    def get_player_by_tg_id(self, tg_user_id: int) -> Optional[Player]:
        try:
            with self.session_maker() as session:
                player = session.execute(
                    select(Player)
                    .join(User)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).first()
            return player if player is None else player[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting player from database: {e}")

    def get_all_players(self, offset: int, limit: int) -> list[Player]:
        try:
            with self.session_maker() as session:
                players = session.execute(
                    select(Player)
                    .order_by(Player.id.asc())
                    .offset(offset)
                    .limit(limit)
                ).all()
            return [player_[0] for player_ in players]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting all players from database: {e}")

    def update_player_balance_by_id(self, player_id: int, amount: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                result = session.execute(
                    update(Player)
                    .where(Player.id == player_id)
                    .values(balance=Player.balance + amount)
                ).rowcount
            return result != 0
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while updating player balance by id in database: {e}")

    def update_player_balance_by_tg_id(self, tg_user_id: int, amount: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                player_id = (
                    select(Player.id)
                    .join(User)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).scalar_subquery()
                result = session.execute(
                    update(Player)
                    .where(Player.id == player_id)
                    .values(balance=Player.balance + amount)
                ).rowcount
            return result != 0
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while updating player balance by tg_id in database: {e}")

    def transfer_by_id(self, from_player_id: int, to_player_id: int, amount: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                result = session.execute(
                    update(Player)
                    .where(Player.id == from_player_id)
                    .values(balance=Player.balance - amount)
                ).rowcount
                if result != 0:
                    result = session.execute(
                        update(Player)
                        .where(Player.id == to_player_id)
                        .values(balance=Player.balance + amount)
                    ).rowcount
                if result == 0:
                    session.rollback()
            return result != 0
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while transferring money between players in database: {e}")

    def transfer_by_tg_id(self, from_user_tg_id: int, to_user_tg_id: int, amount: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                from_player_id = (
                    select(Player.id)
                    .join(User)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == from_user_tg_id)
                ).scalar_subquery()
                to_player_id = (
                    select(Player.id)
                    .join(User)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == to_user_tg_id)
                ).scalar_subquery()
                result = session.execute(
                    update(Player)
                    .where(Player.id == from_player_id)
                    .values(balance=Player.balance - amount)
                ).rowcount
                if result != 0:
                    result = session.execute(
                        update(Player)
                        .where(Player.id == to_player_id)
                        .values(balance=Player.balance + amount)
                    ).rowcount
                if result == 0:
                    session.rollback()
            return result != 0
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while transferring money between players in database: {e}")

    def check_manager_name_availability(self, name: str) -> bool:
        try:
            with self.session_maker() as session:
                result = session.execute(
                    select(User)
                    .where(User.name == name)
                ).first()
            return result is None
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while checking manager name availability in database: {e}")

    def add_manager(self, tg_user_id: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                user_id = (
                    select(User.id)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).scalar_subquery()
                session.execute(
                    insert(Manager)
                    .values(user_id=user_id)
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding manager to database: {e}")

    def get_manager_by_id(self, manager_id: int) -> Optional[Manager]:
        try:
            with self.session_maker() as session:
                manager = session.execute(
                    select(Manager)
                    .where(Manager.id == manager_id)
                ).first()
            return manager if manager is None else manager[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting manager from database: {e}")

    def get_manager_by_tg_id(self, tg_user_id: int) -> Optional[Manager]:
        try:
            with self.session_maker() as session:
                manager = session.execute(
                    select(Manager)
                    .join(User)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).first()
            return manager if manager is None else manager[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting manager from database: {e}")

    def update_manager_location_by_id(self, manager_id: int, location_id: Optional[int] = None) -> bool:
        try:
            with self.session_maker.begin() as session:
                result = session.execute(
                    update(Manager)
                    .where(Manager.id == manager_id)
                    .values(location_id=location_id)
                ).rowcount
            return result != 0
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while updating manager location by id in database: {e}")

    def update_manager_location_by_tg_id(self, tg_user_id: int, location_id: Optional[int] = None) -> bool:
        try:
            with self.session_maker.begin() as session:
                manager_id = (
                    select(Manager.id)
                    .join(User)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).scalar_subquery()
                result = session.execute(
                    update(Manager)
                    .where(Manager.id == manager_id)
                    .values(location_id=location_id)
                ).rowcount
            return result != 0
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while updating manager location by tg_id in database: {e}")

    def add_managers_blacklist_record(self, tg_user_id: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                tg_account_id = (
                    select(TelegramAccount.id)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).scalar_subquery()
                session.execute(
                    insert(ManagersBlacklistRecord)
                    .values(tg_account_id=tg_account_id)
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding managers blacklist record to database: {e}")

    def get_managers_blacklist_record(self, tg_user_id: int) -> Optional[ManagersBlacklistRecord]:
        try:
            with self.session_maker() as session:
                record = session.execute(
                    select(ManagersBlacklistRecord)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).first()
            return record if record is None else record[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting managers blacklist record from database: {e}")

    def delete_managers_blacklist_record(self, tg_user_id: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                tg_account_id = (
                    select(TelegramAccount.id)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).scalar_subquery()
                result = session.execute(
                    delete(ManagersBlacklistRecord)
                    .where(ManagersBlacklistRecord.tg_account_id == tg_account_id)
                ).rowcount
            return result != 0
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while removing managers blacklist record from database: {e}")

    def add_location(self, name: str, max_reward: int, is_onetime: bool) -> bool:
        try:
            with self.session_maker.begin() as session:
                session.execute(
                    insert(Location)
                    .values(name=name, max_reward=max_reward, is_onetime=is_onetime)
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding location to database: {e}")

    def get_location_by_id(self, location_id: int) -> Optional[Location]:
        try:
            with self.session_maker() as session:
                location = session.execute(
                    select(Location)
                    .where(Location.id == location_id)
                ).first()
            return location if location is None else location[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting location from database: {e}")

    def get_location_by_manager_id(self, manager_id: int) -> Optional[Location]:
        try:
            with self.session_maker() as session:
                location = session.execute(
                    select(Location)
                    .join(Manager)
                    .where(Manager.id == manager_id)
                ).first()
            return location if location is None else location[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting location from database: {e}")

    def get_location_by_manager_tg_id(self, tg_user_id: int) -> Optional[Location]:
        try:
            with self.session_maker() as session:
                location = session.execute(
                    select(Location)
                    .join(Manager)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).first()
            return location if location is None else location[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting location from database: {e}")

    def get_all_locations(self, offset: int, limit: int) -> list[tuple[Location, int]]:
        try:
            with self.session_maker() as session:
                locations = session.execute(
                    select(Location, func.count(QueueEntry.id))
                    .outerjoin(QueueEntry)
                    .group_by(Location.id)
                    .order_by(func.count(QueueEntry.id).desc())
                    .offset(offset)
                    .limit(limit)
                ).all()
            return [location_[0] for location_ in locations]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting all locations from database: {e}")

    def add_shop(self, location_id: int, name: str) -> bool:
        try:
            with self.session_maker.begin() as session:
                session.execute(
                    insert(Shop)
                    .values(location_id=location_id, name=name)
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding shop to database: {e}")

    def get_shop_by_id(self, shop_id: int) -> Optional[Shop]:
        try:
            with self.session_maker() as session:
                shop = session.execute(
                    select(Shop)
                    .where(Shop.id == shop_id)
                ).first()
            return shop if shop is None else shop[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting shop from database: {e}")

    def add_queue_entry_by_player_id(self, player_id: int, location_id: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                session.execute(
                    insert(QueueEntry)
                    .values(location_id=location_id, player_id=player_id)
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding queue to database: {e}")

    def add_queue_entry_by_tg_id(self, tg_user_id: int, location_id: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                player_id = (
                    select(Player.id)
                    .join(User)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).scalar_subquery()
                session.execute(
                    insert(QueueEntry)
                    .values(location_id=location_id, player_id=player_id)
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding queue to database: {e}")

    def get_queue_entry_by_player_id(self, player_id: int) -> Optional[QueueEntry]:
        try:
            with self.session_maker() as session:
                queue = session.execute(
                    select(QueueEntry)
                    .where(QueueEntry.player_id == player_id)
                ).first()
            return queue if queue is None else queue[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting queue from database: {e}")

    def get_queue_entry_by_tg_id(self, tg_user_id: int) -> Optional[QueueEntry]:
        try:
            with self.session_maker() as session:
                queue = session.execute(
                    select(QueueEntry)
                    .join(Player)
                    .join(User)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).first()
            return queue if queue is None else queue[0]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting queue from database: {e}")

    def get_queue_by_location_id(self, location_id: int, offset: int, limit: int) -> list[QueueEntry]:
        try:
            with self.session_maker() as session:
                queue = session.execute(
                    select(QueueEntry)
                    .where(QueueEntry.location_id == location_id)
                    .order_by(QueueEntry.id.asc())
                    .offset(offset)
                    .limit(limit)
                ).all()
            return [queue_entry_[0] for queue_entry_ in queue]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting queues from database: {e}")

    def delete_queue_entry_by_player_id(self, player_id: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                result = session.execute(
                    delete(QueueEntry)
                    .where(QueueEntry.player_id == player_id)
                ).rowcount
            return result != 0
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while removing queue from database: {e}")

    def delete_queue_entry_by_tg_id(self, tg_user_id: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                player_id = (
                    select(Player.id)
                    .join(User)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).scalar_subquery()
                result = session.execute(
                    delete(QueueEntry)
                    .where(QueueEntry.player_id == player_id)
                ).rowcount
            return result != 0
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while removing queue from database: {e}")

    def add_finished_location_by_player_id(self, player_id: int, location_id: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                session.execute(
                    insert(FinishedLocation)
                    .values(location_id=location_id, player_id=player_id)
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding finished location to database: {e}")

    def add_finished_location_by_tg_id(self, tg_user_id: int, location_id: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                player_id = (
                    select(Player.id)
                    .join(User)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).scalar_subquery()
                session.execute(
                    insert(FinishedLocation)
                    .values(location_id=location_id, player_id=player_id)
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding finished location to database: {e}")

    def get_finished_locations_by_player_id(self, player_id: int) -> list[FinishedLocation]:
        try:
            with self.session_maker() as session:
                finished_locations = session.execute(
                    select(FinishedLocation)
                    .where(FinishedLocation.player_id == player_id)
                ).all()
            return [finished_location_[0] for finished_location_ in finished_locations]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting finished locations from database: {e}")

    def get_finished_locations_by_tg_id(self, tg_user_id: int) -> list[FinishedLocation]:
        try:
            with self.session_maker() as session:
                finished_locations = session.execute(
                    select(FinishedLocation)
                    .join(Player)
                    .join(User)
                    .join(TelegramAccount)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).all()
            return [finished_location_[0] for finished_location_ in finished_locations]
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while getting finished locations from database: {e}")

    def add_transfer_record(self, from_player_id: int, to_player_id: int, amount: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                session.execute(
                    insert(TransferRecord)
                    .values(from_player_id=from_player_id, to_player_id=to_player_id, amount=amount)
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding transfer record to database: {e}")

    def add_reward_record(self, player_id: int, location_id: int, manager_id: int, amount: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                session.execute(
                    insert(RewardRecord)
                    .values(
                        recipient_player_id=player_id,
                        location_id=location_id,
                        conducted_by_manager_id=manager_id,
                        amount=amount
                    )
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding reward record to database: {e}")

    def add_purchase_record(self, player_id: int, shop_id: int, manager_id: int, amount: int) -> bool:
        try:
            with self.session_maker.begin() as session:
                session.execute(
                    insert(PurchaseRecord)
                    .values(
                        customer_player_id=player_id,
                        shop_id=shop_id,
                        conducted_by_manager_id=manager_id,
                        amount=amount
                    )
                )
            return True
        except IntegrityError:
            return False
        except SQLAlchemyError as e:
            self.logger.exception(e)
            raise DBError(f"Error occurred while adding purchase record to database: {e}")
