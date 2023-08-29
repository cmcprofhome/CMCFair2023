import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class DBAdapter:
    def __init__(self, user: str, password: str, host: str, port: int, database: str, logger: logging.Logger):
        self.logger = logger

        self.engine = create_engine(f'postgresql+psycopg://{user}:{password}@{host}:{port}/{database}')
        self.session_maker = sessionmaker(self.engine)
