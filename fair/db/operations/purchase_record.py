from sqlalchemy import insert
from sqlalchemy.orm import Session

from fair.db.models import PurchaseRecord


def add(session: Session, player_id: int, shop_id: int, manager_id: int, amount: int) -> bool:
    session.execute(
        insert(PurchaseRecord)
        .values(
            customer_player_id=player_id,
            shop_id=shop_id,
            conducted_by_manager_id=manager_id,
            amount=amount
        )
    )
    return True
