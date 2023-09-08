from typing import Optional

from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from fair.db.models import Role, TelegramAccount, User


def add(session: Session, role_name: str, tg_user_id: int, user_name: str) -> bool:
    role_id = (
        select(Role.id)
        .where(Role.name == role_name)
    ).scalar_subquery()
    tg_account_id = (
        select(TelegramAccount.id)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).scalar_subquery()
    session.execute(
        insert(User)
        .values(role_id=role_id, name=user_name, tg_account_id=tg_account_id)
    )
    return True


def get_by_id(session: Session, user_id: int) -> Optional[User]:
    user = session.execute(
        select(User)
        .where(User.id == user_id)
    ).first()
    return user if user is None else user[0]


def get_by_tg_id(session: Session, tg_user_id: int) -> Optional[User]:
    user = session.execute(
        select(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).first()
    return user if user is None else user[0]
