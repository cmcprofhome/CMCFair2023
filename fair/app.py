import os

from sanic import Sanic

from fair.bot import setup_bot, launch_bot, stop_bot
from fair.config import load_config
from fair.db import setup_adapter
from fair.logger import setup_logger
from fair.routes import setup_routes


async def on_startup(app: Sanic):
    bot = app.ctx['bot']
    cfg = app.ctx['bot_config']
    launch_bot(bot, cfg.drop_pending, cfg.use_webhook, cfg.allowed_updates, cfg.webhook)


async def on_shutdown(app: Sanic):
    bot = app.ctx['bot']
    cfg = app.ctx['bot_config']
    stop_bot(bot, cfg.use_webhook)


def build_app() -> Sanic:
    app = Sanic("FairBotApp")
    config_path = os.environ.get('CONFIG_PATH', './config.toml')
    use_env_vars = os.environ.get('USE_ENV_VARS', True)
    config_env_mapping_path = os.environ.get('CONFIG_ENV_MAPPING_PATH', None)
    cfg = load_config(config_path, use_env_vars, config_env_mapping_path)
    app.ctx['bot_config'] = cfg.bot
    db_logger = setup_logger(cfg.db.logger)
    db_adapter = setup_adapter(cfg.db, db_logger)
    bot_logger = setup_logger(cfg.bot.logger)
    bot = setup_bot(cfg.bot, db_adapter, cfg.messages, cfg.buttons, bot_logger)
    app.ctx['bot'] = bot

    setup_routes(app)
    app.before_server_start(on_startup)
    app.after_server_stop(on_shutdown)
    return app
