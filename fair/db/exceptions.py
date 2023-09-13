from sqlalchemy.exc import SQLAlchemyError


class DBError(SQLAlchemyError):
    def __init__(self, message: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message

    def __str__(self):
        return self.message
