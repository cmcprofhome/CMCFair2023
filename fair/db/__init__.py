from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

from fair.config import DBConfig

from fair.db.adapter import DBAdapter
from fair.db.exceptions import DBError


def setup_session_maker(db_config: DBConfig):
    db_url = URL.create(
        drivername="postgresql+psycopg",
        username=db_config.user,
        password=db_config.password,
        host=db_config.host,
        port=db_config.port,
        database=db_config.database
    )
    db_engine = create_engine(db_url)
    db_session_maker = sessionmaker(bind=db_engine)
    return db_session_maker
