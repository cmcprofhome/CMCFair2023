from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker

from fair.config import DBConfig
from fair.logger import setup_logger

from fair.db.adapter import DBAdapter
from fair.db.exceptions import DBError


def setup_adapter(db_config: DBConfig):
    db_logger = setup_logger(db_config.logger)
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
    db_adapter = DBAdapter(session_maker=db_session_maker, logger=db_logger)
    return db_adapter
