from sqlalchemy import Boolean, Integer, BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship


class BaseModel(DeclarativeBase):
    pass


class Role(BaseModel):
    __tablename__ = 'roles'

    # PK and FKs
    id = mapped_column(Integer, primary_key=True)

    # Data columns
    name = mapped_column(String(255), unique=True, nullable=False)


class TelegramAccount(BaseModel):
    __tablename__ = 'telegram_accounts'

    # PK and FKs
    id = mapped_column(Integer, primary_key=True)

    # Data columns
    tg_user_id = mapped_column(BigInteger, unique=True, nullable=False)
    tg_chat_id = mapped_column(BigInteger, unique=True, nullable=False)
    tg_username = mapped_column(String(255), nullable=True)


class User(BaseModel):
    __tablename__ = 'users'

    # PK and FKs
    id = mapped_column(Integer, primary_key=True)
    role_id = mapped_column(ForeignKey("roles.id"), nullable=False)
    tg_account_id = mapped_column(ForeignKey("telegram_accounts.id"), unique=True, nullable=False)

    # Data columns
    name = mapped_column(String(255), unique=True, nullable=False)

    # Relationships
    role = relationship("Role")
    tg_account = relationship("TelegramAccount")


class Player(BaseModel):
    __tablename__ = 'players'

    # PK and FKs
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)

    # Data columns
    balance = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    user = relationship("User")
    queue = relationship("Queue")
    finished_locations = relationship("FinishedLocation")


class Manager(BaseModel):
    __tablename__ = 'managers'

    # PK and FKs
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    location_id = mapped_column(ForeignKey("locations.id"), nullable=True)

    # Relationships
    user = relationship("User")
    location = relationship("Location")


class ManagersBlacklistRecord(BaseModel):
    __tablename__ = 'managers_blacklist'

    # PK and FKs
    id = mapped_column(Integer, primary_key=True)
    tg_account_id = mapped_column(ForeignKey("telegram_accounts.id"), unique=True, nullable=False)

    # Relationships
    tg_account = relationship("TelegramAccount")


class Location(BaseModel):
    __tablename__ = 'locations'

    # PK and FKs
    id = mapped_column(Integer, primary_key=True)

    # Data columns
    name = mapped_column(String(255), unique=True, nullable=False)
    max_reward = mapped_column(Integer, default=100, nullable=False)
    is_onetime = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    queues = relationship("Queue")


class Shop(BaseModel):
    __tablename__ = 'shops'

    # PK and FKs
    id = mapped_column(Integer, primary_key=True)
    location_id = mapped_column(ForeignKey("locations.id"), unique=True, nullable=False)

    # Data columns
    name = mapped_column(String(255), unique=True, nullable=False)

    # Relationships
    location = relationship("Location")


class Queue(BaseModel):
    __tablename__ = 'queues'

    # PK and FKs
    id = mapped_column(Integer, primary_key=True)
    player_id = mapped_column(ForeignKey("players.id"), unique=True, nullable=False)
    location_id = mapped_column(ForeignKey("locations.id"), nullable=False)


class FinishedLocation(BaseModel):
    __tablename__ = 'finished_locations'

    # PK and FKs
    player_id = mapped_column(ForeignKey("players.id"), primary_key=True)
    location_id = mapped_column(ForeignKey("locations.id"), primary_key=True)


class TransferRecord(BaseModel):
    __tablename__ = 'transfers_history'

    # PK and FKs
    id = mapped_column(Integer, primary_key=True)
    sender_player_id = mapped_column(ForeignKey("players.id"), nullable=False)
    receiver_player_id = mapped_column(ForeignKey("players.id"), nullable=False)

    # Data columns
    amount = mapped_column(Integer, nullable=False)


class RewardRecord(BaseModel):
    __tablename__ = 'rewards_history'

    # PK and FKs
    id = mapped_column(Integer, primary_key=True)
    recipient_player_id = mapped_column(ForeignKey("players.id"), nullable=False)
    location_id = mapped_column(ForeignKey("locations.id"), nullable=False)
    conducted_by_manager_id = mapped_column(ForeignKey("managers.id"), nullable=False)

    # Data columns
    amount = mapped_column(Integer, nullable=False)


class PurchaseRecord(BaseModel):
    __tablename__ = 'purchases_history'

    # PK and FKs
    id = mapped_column(Integer, primary_key=True)
    customer_player_id = mapped_column(ForeignKey("players.id"), nullable=False)
    shop_id = mapped_column(ForeignKey("shops.id"), nullable=False)
    conducted_by_manager_id = mapped_column(ForeignKey("managers.id"), nullable=False)

    # Data columns
    amount = mapped_column(Integer, nullable=False)
