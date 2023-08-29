from fair.config import DBConfig
from fair.logger import setup_logger

from fair.db.adapter import DBAdapter


def setup_adapter(db_config: DBConfig):
    db_logger = setup_logger(db_config.logger)
    db_adapter = DBAdapter(
        user=db_config.user,
        password=db_config.password,
        host=db_config.host,
        port=db_config.port,
        database=db_config.database,
        logger=db_logger
    )
    return db_adapter
