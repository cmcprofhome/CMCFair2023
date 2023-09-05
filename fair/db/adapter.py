import logging
from typing import Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from fair.db.exceptions import DBError
from fair.db.models import (
    Role, TelegramAccount,
    User, Player, Manager,
    ManagersBlacklistRecord,
    Location, Shop,
    Queue, FinishedLocation,
    TransferRecord, RewardRecord, PurchaseRecord
)


class DBAdapter:
    def __init__(self, user: str, password: str, host: str, port: int, database: str, logger: logging.Logger):
        self.logger = logger

        self.engine = create_engine(f'postgresql+psycopg://{user}:{password}@{host}:{port}/{database}')
        self.session_maker = sessionmaker(self.engine)

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
                tg_account_id = session.execute(
                    select(TelegramAccount.id)
                    .where(TelegramAccount.tg_user_id == tg_user_id)
                ).first()
                if tg_account_id is None:
                    raise DBError(f"Telegram account with tg_user_id '{tg_user_id}' does not exist!")
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
