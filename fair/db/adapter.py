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
