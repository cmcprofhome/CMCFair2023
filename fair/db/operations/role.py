from sqlalchemy import insert, delete
from sqlalchemy.orm import Session

from fair.db.models import Role


def add(session: Session, name: str) -> bool:
    session.execute(
        insert(Role)
        .values(name=name)
    )
    return True


def delete_by_name(session: Session, name: str) -> bool:
    session.execute(
        delete(Role)
        .where(Role.name == name)
    )
    return True
