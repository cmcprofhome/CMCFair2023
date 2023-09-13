from typing import Optional

from sqlalchemy import select, insert, delete
from sqlalchemy.orm import Session

from fair.db.models import TelegramAccount, ManagersBlacklistRecord


def add(session: Session, tg_user_id: int) -> bool:
    tg_account_id = (
        select(TelegramAccount.id)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).scalar_subquery()
    session.execute(
        insert(ManagersBlacklistRecord)
        .values(tg_account_id=tg_account_id)
    )
    return True


def get_by_tg_id(session: Session, tg_user_id: int) -> Optional[ManagersBlacklistRecord]:
    record = session.execute(
        select(ManagersBlacklistRecord)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).first()
    return record if record is None else record[0]


def delete_by_tg_id(session: Session, tg_user_id: int) -> bool:
    tg_account_id = (
        select(TelegramAccount.id)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).scalar_subquery()
    result = session.execute(
        delete(ManagersBlacklistRecord)
        .where(ManagersBlacklistRecord.tg_account_id == tg_account_id)
    ).rowcount
    return result != 0
