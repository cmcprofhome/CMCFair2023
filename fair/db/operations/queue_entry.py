from typing import Optional, Union

from sqlalchemy import select, insert, delete, func, ScalarSelect
from sqlalchemy.orm import Session

from fair.db.models import TelegramAccount, User, Player, Manager, QueueEntry


def add_by_player_id(session: Session, player_id: Union[int, ScalarSelect], location_id: int) -> bool:
    session.execute(
        insert(QueueEntry)
        .values(location_id=location_id, player_id=player_id)
    )
    return True


def add_by_player_tg_id(session: Session, tg_user_id: int, location_id: int) -> bool:
    player_id = (
        select(Player.id)
        .join(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).scalar_subquery()
    return add_by_player_id(session, player_id, location_id)


def get_by_player_id(session: Session, player_id: int) -> Optional[QueueEntry]:
    queue = session.execute(
        select(QueueEntry)
        .where(QueueEntry.player_id == player_id)
    ).first()
    return queue if queue is None else queue[0]


def get_by_player_tg_id(session: Session, tg_user_id: int) -> Optional[QueueEntry]:
    queue = session.execute(
        select(QueueEntry)
        .join(Player)
        .join(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).first()
    return queue if queue is None else queue[0]


def get_by_location_id(
        session: Session,
        location_id: Union[int, ScalarSelect],
        offset: int,
        limit: int) -> list[Player]:
    queue_players = session.execute(
        select(Player)
        .join(QueueEntry)
        .where(QueueEntry.location_id == location_id)
        .order_by(QueueEntry.id.asc())
        .offset(offset)
        .limit(limit)
    ).all()
    return [player_[0] for player_ in queue_players]


def get_by_manager_id(session: Session, manager_id: int, offset: int, limit: int) -> list[Player]:
    location_id = (
        select(Manager.location_id)
        .where(Manager.id == manager_id)
    ).scalar_subquery()
    return get_by_location_id(session, location_id, offset, limit)


def get_by_manager_tg_id(session: Session, tg_user_id: int, offset: int, limit: int) -> list[Player]:
    location_id = (
        select(Manager.location_id)
        .join(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).scalar_subquery()
    return get_by_location_id(session, location_id, offset, limit)


def delete_by_player_id(session: Session, player_id: Union[int, ScalarSelect]) -> bool:
    result = session.execute(
        delete(QueueEntry)
        .where(QueueEntry.player_id == player_id)
    ).rowcount
    return result != 0


def delete_by_player_tg_id(session: Session, tg_user_id: int) -> bool:
    player_id = (
        select(Player.id)
        .join(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).scalar_subquery()
    return delete_by_player_id(session, player_id)
