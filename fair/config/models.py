from dataclasses import dataclass
from typing import Literal, Optional, Union


@dataclass
class LoggerConfig:
    name: str
    level: Literal['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']  # Log level
    stream: Optional[Literal['stdout', 'stderr']] = None  # Log stream if any
    file_path: Optional[str] = None  # Log file path if any
    format: Optional[str] = None  # Log format if any


@dataclass
class RedisConfig:
    host: str
    port: int
    db: Optional[int] = 0
    password: Optional[str] = None
    prefix: Optional[str] = 'telebot_'


@dataclass
class BotStateStorageConfig:
    type: Literal['redis', 'memory']  # State storage type, I don't recommend using pickle, thus leave it out
    redis: Optional[RedisConfig] = None  # Redis config if any


@dataclass
class BotWebhookConfig:
    url: str  # Webhook url to send updates to
    secret_token: str  # Secret token to verify the webhook, strongly recommended
    cert_path: Optional[str] = None  # Path to the public key SSL certificate if self-signed
    ip_address: Optional[str] = None  # IP address to use instead of one resolved via DNS
    max_connections: Optional[int] = None  # Maximum allowed number of simultaneous HTTPS connections to the webhook


@dataclass
class BotConfig:
    owner_tg_id: int  # Bot owner telegram id
    token: str  # Telegram bot token
    drop_pending: bool  # Drop pending updates on startup
    use_webhook: bool  # Use webhook, otherwise long polling
    use_class_middlewares: bool  # Use class middlewares if any
    actions_timeout: float  # Timeout between user's actions in seconds
    page_size: int  # Page size for pagination in inline keyboards
    logger: LoggerConfig  # Logger config for the bot
    allowed_updates: Optional[Union[list[str], Literal['ALL']]] = None  # by default all except chat_member
    state_storage: Optional[BotStateStorageConfig] = None  # Bot state storage config if any
    webhook: Optional[BotWebhookConfig] = None  # Webhook config if any
    telegram_api_url: Optional[str] = None  # Custom Telegram API url for Local Bot API Server if any


@dataclass
class DBConfig:
    host: str  # DBMS host
    port: int  # DBMS port
    user: str  # DBMS user
    password: str  # DBMS user password
    database: str  # Database name
    logger: LoggerConfig  # Logger config for database


@dataclass
class MessagesConfig:
    welcome: str
    unregistered_help: str
    player_help: str
    manager_help: str
    owner_help: str
    anti_flood: str
    get_player_name: str
    invalid_player_name: str
    player_name_already_taken: str
    player_registered: str
    player_balance: str
    choose_money_transfer_recipient: str
    money_transfer_recipient_cancelled: str
    choose_money_transfer_amount: str
    money_transfer_success: str
    choose_new_queue_location: str
    new_queue_location_cancelled: str
    queue_entry_added: str
    player_queue_location: str
    player_left_queue: str
    manager_registration_forbidden: str
    manager_registration_disabled: str
    get_manager_password: str
    get_manager_name: str
    invalid_manager_name: str
    manager_name_already_taken: str
    manager_registered: str
    all_players: str
    all_players_cancelled: str
    all_locations: str
    all_locations_cancelled: str
    choose_add_balance_recipient: str
    add_balance_cancelled: str
    choose_add_balance_amount: str
    choose_subtract_balance_recipient: str
    subtract_balance_cancelled: str
    choose_subtract_balance_amount: str
    choose_reward_recipient: str
    reward_cancelled: str
    choose_reward_amount: str
    reward_successful: str
    choose_purchase_recipient: str
    purchase_cancelled: str
    choose_purchase_amount: str
    purchase_successful: str
    choose_location: str
    choose_location_cancelled: str
    location_updated: str
    chosen_location: str
    my_location_queue: str
    my_location_queue_cancelled: str
    location_player_chosen_options: str
    location_paused: str
    location_unpaused: str
    manager_my_location: str
    manager_left_location: str
    manager_password_set: str
    manager_password_reset: str
    location_added: str
    invalid_add_location_args: str
    add_player_error: str
    player_not_found_error: str
    player_not_in_queue_error: str
    queue_entry_already_exists_error: str
    money_transfer_recipient_not_chosen_error: str
    money_transfer_amount_invalid_error: str
    add_manager_error: str
    manager_not_on_location_error: str
    bad_location_error: str
    pause_location_error: str
    unpause_location_error: str
    bad_player_balance_error: str
    bad_chosen_player_error: str
    bad_manager_error: str
    add_user_error: str
    add_tg_account_error: str
    unknown_error: str


@dataclass
class ButtonsConfig:
    reg_player: str
    reg_manager: str
    new_queue: str
    my_balance: str
    transfer_money: str
    my_queue: str
    leave_queue: str
    list_all_players: str
    list_all_locations: str
    add_balance: str
    subtract_balance: str
    choose_location: str
    reward_player: str
    purchase: str
    my_location: str
    my_location_queue: str
    leave_location: str
    pause_location: str
    unpause_location: str
    prev_page: str
    next_page: str
    help: str
    cancel: str


@dataclass
class Config:
    bot: BotConfig
    db: DBConfig
    # Extra configs if any
    logger: LoggerConfig  # Logger config for the app
    messages: MessagesConfig  # Messages text config
    buttons: ButtonsConfig  # Buttons text config
