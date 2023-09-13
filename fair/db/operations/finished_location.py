from typing import Union

from sqlalchemy import select, insert, ScalarSelect
from sqlalchemy.orm import Session

from fair.db.models import TelegramAccount, User, Player, FinishedLocation


def add_by_player_id(session: Session, player_id: Union[int, ScalarSelect], location_id: int) -> bool:
    session.execute(
        insert(FinishedLocation)
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


def get_by_player_id(session: Session, player_id: int) -> list[FinishedLocation]:
    finished_locations = session.execute(
        select(FinishedLocation)
        .where(FinishedLocation.player_id == player_id)
    ).all()
    return [finished_location_[0] for finished_location_ in finished_locations]


def get_by_player_tg_id(session: Session, tg_user_id: int) -> list[FinishedLocation]:
    finished_locations = session.execute(
        select(FinishedLocation)
        .join(Player)
        .join(User)
        .join(TelegramAccount)
        .where(TelegramAccount.tg_user_id == tg_user_id)
    ).all()
    return [finished_location_[0] for finished_location_ in finished_locations]
