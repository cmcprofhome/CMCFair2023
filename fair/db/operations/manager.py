from typing import Optional, Union

from sqlalchemy import select, insert, update, delete, ScalarSelect
from sqlalchemy.orm import Session

from fair.db.models import TelegramAccount, User, Manager, Location


def check_name_availability(session: Session, name: str) -> bool:
    result = session.execute(
        select(Manager.id)
        .where(Manager.name == name)
    ).first()
    return result is None


def add(session: Session, tg_user_id: int, name: str) -> bool:
    user_id = (
        select(User.id)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).scalar_subquery()
    session.execute(
        insert(Manager)
        .values(user_id=user_id, name=name)
    )
    return True


def get_by_id(session: Session, manager_id: int) -> Optional[Manager]:
    manager = session.execute(
        select(Manager)
        .where(Manager.id == manager_id)
    ).first()
    return manager if manager is None else manager[0]


def get_by_tg_id(session: Session, tg_user_id: int) -> Optional[Manager]:
    manager = session.execute(
        select(Manager)
        .join(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).first()
    return manager if manager is None else manager[0]


def update_location_by_id(
        session: Session,
        manager_id: Union[int, ScalarSelect],
        new_location_id: Optional[int] = None) -> bool:
    if new_location_id is None:
        location_id = (
            select(Location.id)
            .join(Manager)
            .where(Manager.id == manager_id)
        ).scalar_subquery()
    else:
        location_id = new_location_id
    result = session.execute(
        update(Location)
        .where(Location.id == location_id)
        .values(is_active=new_location_id is not None)
    ).rowcount
    if result != 0:
        result = session.execute(
            update(Manager)
            .where(Manager.id == manager_id)
            .values(location_id=new_location_id)
        ).rowcount
    return result != 0


def update_location_by_tg_id(session: Session, tg_user_id: int, new_location_id: Optional[int] = None) -> bool:
    manager_id = (
        select(Manager.id)
        .join(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).scalar_subquery()
    return update_location_by_id(session, manager_id, new_location_id)


def delete_by_tg_id(session: Session, tg_user_id: int) -> bool:
    manager_id = (
        select(Manager.id)
        .join(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).scalar_subquery()
    result = session.execute(
        delete(Manager)
        .where(Manager.id == manager_id)
    ).rowcount
    return result != 0
