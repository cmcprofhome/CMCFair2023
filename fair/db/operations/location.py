from typing import Optional, Union

from sqlalchemy import select, insert, update, func, ScalarSelect
from sqlalchemy.orm import Session

from fair.db.models import TelegramAccount, User, Manager, Location, QueueEntry


def add(session: Session, name: str, max_reward: int, is_onetime: bool) -> bool:
    session.execute(
        insert(Location)
        .values(name=name, max_reward=max_reward, is_onetime=is_onetime)
    )
    return True


def get_by_id(session: Session, location_id: int) -> Optional[Location]:
    location = session.execute(
        select(Location)
        .where(Location.id == location_id)
    ).first()
    return location if location is None else location[0]


def get_by_manager_id(session: Session, manager_id: int) -> Optional[Location]:
    location = session.execute(
        select(Location)
        .join(Manager)
        .where(Manager.id == manager_id)
    ).first()
    return location if location is None else location[0]


def get_by_manager_tg_id(session: Session, tg_user_id: int) -> Optional[Location]:
    location = session.execute(
        select(Location)
        .join(Manager)
        .join(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).first()
    return location if location is None else location[0]


def get_all(session: Session, offset: int, limit: int) -> list[tuple[Location, int]]:
    locations = session.execute(
        select(Location, func.count(QueueEntry.id))
        .outerjoin(QueueEntry)
        .group_by(Location.id)
        .order_by(func.count(QueueEntry.id).desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return [location_[0] for location_ in locations]


def get_all_count(session: Session) -> int:
    locations_cnt = session.execute(
        select(func.count(Location))
    ).first()
    return locations_cnt[0]


def get_all_active(session: Session, offset: int, limit: int) -> list[tuple[Location, int]]:
    locations = session.execute(
        select(Location, func.count(QueueEntry.id))
        .outerjoin(QueueEntry)
        .where(Location.is_active is True)
        .group_by(Location.id)
        .order_by(func.count(QueueEntry.id).desc())
        .offset(offset)
        .limit(limit)
    ).all()
    return [location_[0] for location_ in locations]


def get_all_active_count(session: Session) -> int:
    locations_cnt = session.execute(
        select(func.count(Location))
        .where(Location.is_active is True)
    ).first()
    return locations_cnt[0]


def update_by_id(session: Session, location_id: Union[int, ScalarSelect], is_active: bool) -> bool:
    result = session.execute(
        update(Location)
        .where(Location.id == location_id)
        .values(is_active=is_active)
    ).rowcount
    return result != 0


def update_by_manager_id(session: Session, manager_id: int, is_active: bool) -> bool:
    location_id = (
        select(Location.id)
        .join(Manager)
        .where(Manager.id == manager_id)
    ).scalar_subquery()
    return update_by_id(session, location_id, is_active)


def update_by_manager_tg_id(session: Session, tg_user_id: int, is_active: bool) -> bool:
    location_id = (
        select(Location.id)
        .join(Manager)
        .join(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).scalar_subquery()
    return update_by_id(session, location_id, is_active)
