from aiohttp.web import Application, Request, Response
from telebot.types import Update


# TODO: move it to the separate file / module
async def handle_telegram_update(request: Request):
    secret_token = request.app['bot_config'].webhook.secret_token
    if secret_token != request.headers.get('X-Telegram-Bot-Api-Secret-Token'):
        return Response(body='Forbidden', status=403)
    body_json = await request.json()
    bot = request.app['bot']
    bot.process_new_updates([Update.de_json(body_json)])
    return Response(body='OK', status=200)


def setup_routes(app: Application):
    app.router.add_post('/' + app['bot_config'].token, handle_telegram_update)
