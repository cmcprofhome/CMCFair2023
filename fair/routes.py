from sanic import Sanic, Request
from sanic.response import text
from telebot.types import Update


# TODO: move it to the separate file / module
async def handle_telegram_update(request: Request):
    secret_token = request.app.ctx.bot_config.webhook.secret_token
    if secret_token != request.headers.get('X-Telegram-Bot-Api-Secret-Token'):
        return text('Forbidden', status=403)
    body_json = await request.json()
    bot = request.app.ctx.bot
    bot.process_new_updates([Update.de_json(body_json)])
    return text('OK')


def setup_routes(app: Sanic):
    webhook_url = app.ctx.bot_config.webhook.url
    webhook_path = webhook_url.split('/', maxsplit=1)[-1]
    app.add_route(handle_telegram_update, webhook_path, methods=['POST'])
