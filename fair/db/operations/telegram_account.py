from typing import Optional

from sqlalchemy import select, insert, update
from sqlalchemy.orm import Session

from fair.db.models import TelegramAccount


def add(session: Session, tg_user_id: int, tg_chat_id: int, tg_username: Optional[str] = None) -> bool:
    session.execute(
        insert(TelegramAccount)
        .values(tg_user_id=tg_user_id, tg_chat_id=tg_chat_id, tg_username=tg_username)
    )
    return True


def get(session: Session, tg_user_id: int) -> Optional[TelegramAccount]:
    account = session.execute(
                select(TelegramAccount)
                .where(TelegramAccount.tg_user_id == tg_user_id)
            ).first()
    return account if account is None else account[0]


def update_username(session: Session, tg_user_id: int, tg_username: str) -> bool:
    result = session.execute(
                update(TelegramAccount)
                .where(TelegramAccount.tg_user_id == tg_user_id)
                .values(tg_username=tg_username)
            ).rowcount
    return result != 0
