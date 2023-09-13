from sqlalchemy import insert
from sqlalchemy.orm import Session

from fair.db.models import RewardRecord


def add(session: Session, player_id: int, location_id: int, manager_id: int, amount: int) -> bool:
    session.execute(
        insert(RewardRecord)
        .values(
            recipient_player_id=player_id,
            location_id=location_id,
            conducted_by_manager_id=manager_id,
            amount=amount
        )
    )
    return True
