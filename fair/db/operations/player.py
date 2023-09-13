from typing import Optional, Union

from sqlalchemy import select, insert, update, func, ScalarSelect
from sqlalchemy.orm import Session

from fair.db.models import TelegramAccount, User, Player


def check_name_availability(session: Session, name: str) -> bool:
    result = session.execute(
        select(User)
        .where(User.name == name)
    ).first()
    return result is None


def add(session: Session, tg_user_id: int) -> bool:
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


def get_by_id(session: Session, player_id: int) -> Optional[Player]:
    player = session.execute(
        select(Player)
        .where(Player.id == player_id)
    ).first()
    return player if player is None else player[0]


def get_by_tg_id(session: Session, tg_user_id: int) -> Optional[Player]:
    player = session.execute(
        select(Player)
        .join(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).first()
    return player if player is None else player[0]


def get_all(session: Session, offset: int, limit: int) -> list[Player]:
    players = session.execute(
        select(Player)
        .order_by(Player.id.asc())
        .offset(offset)
        .limit(limit)
    ).all()
    return [player_[0] for player_ in players]


def get_all_count(session: Session) -> int:
    players_cnt = session.execute(
        select(func.count(Player))
    ).first()
    return players_cnt[0]


def update_balance_by_id(session: Session, player_id: Union[int, ScalarSelect], amount: int) -> bool:
    result = session.execute(
        update(Player)
        .where(Player.id == player_id)
        .values(balance=Player.balance + amount)
    ).rowcount
    return result != 0


def update_balance_by_tg_id(session: Session, tg_user_id: int, amount: int) -> bool:
    player_id = (
        select(Player.id)
        .join(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).scalar_subquery()
    return update_balance_by_id(session, player_id, amount)


def transfer_by_id(session: Session,
                   from_player_id: Union[int, ScalarSelect],
                   to_player_id: Union[int, ScalarSelect],
                   amount: int) -> bool:
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


def transfer_by_tg_id(session: Session, from_user_tg_id: int, to_user_tg_id: int, amount: int) -> bool:
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
    return transfer_by_id(session, from_player_id, to_player_id, amount)
