from typing import Optional

from sqlalchemy import select, insert
from sqlalchemy.orm import Session

from fair.db.models import Shop, Location


def add(session: Session, location_id: int, name: str) -> bool:
    session.execute(
        insert(Shop)
        .values(location_id=location_id, name=name)
    )
    return True


def get_by_id(session: Session, shop_id: int) -> Optional[Shop]:
    shop = session.execute(
        select(Shop)
        .where(Shop.id == shop_id)
    ).first()
    return shop if shop is None else shop[0]


def get_by_location_id(session: Session, location_id: int) -> Optional[Shop]:
    shop = session.execute(
        select(Shop)
        .join(Location)
        .where(Location.id == location_id)
    ).first()
    return shop if shop is None else shop[0]
