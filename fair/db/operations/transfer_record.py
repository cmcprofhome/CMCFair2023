from sqlalchemy import insert
from sqlalchemy.orm import Session

from fair.db.models import TransferRecord


def add(session: Session, from_player_id: int, to_player_id: int, amount: int) -> bool:
    session.execute(
        insert(TransferRecord)
        .values(from_player_id=from_player_id, to_player_id=to_player_id, amount=amount)
    )
    return True
