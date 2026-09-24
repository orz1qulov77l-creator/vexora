"""
KINO BOT - asosiy ishga tushirish fayli.

Ishlash tartibi:
  1. SQLite baza ishga tushiriladi (init_db)
  2. Render'ning $PORT portida oddiy HTTP server ochiladi - bu Render'ga
     "servis tirik" ekanini bildiradi va UptimeRobot shu manzilga har
     5 daqiqada HEAD so'rov yuborib, botni "uxlab qolishdan" saqlaydi.
  3. Bot polling rejimida ishga tushadi.
  4. Fonda premium muddatini kuzatuvchi vazifa ishga tushadi.

Render.com'da sozlash:
  - Build Command:  pip install -r requirements.txt
  - Start Command:  python bot.py
  - Environment:    BOT_TOKEN, ADMIN_ID (majburiy)
  - Type: Web Service (Free) - $PORT o'zgaruvchisini Render avtomatik beradi
"""
import asyncio
import logging

from aiohttp import web

from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
import database as db
import scheduler
from handlers import admin as admin_handlers
from handlers import user as user_handlers
from middlewares import SubscriptionMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("bot")


def build_router() -> Router:
    router = Router()
    router.message.middleware(SubscriptionMiddleware())
    router.callback_query.middleware(SubscriptionMiddleware())
    user_handlers.register(router)
    admin_handlers.register(router)
    return router


async def _health(request: web.Request) -> web.Response:
    return web.Response(text="OK")


async def _start_web_server() -> web.AppRunner:
    app = web.Application()
    app.router.add_get("/", _health)  # aiohttp GET yo'nalishi HEAD so'rovlarini ham avtomatik qo'llab-quvvatlaydi
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", config.PORT)
    await site.start()
    logger.info("HTTP keep-alive server %s portida ishga tushdi", config.PORT)
    return runner


async def main() -> None:
    db.init_db()
    logger.info("Ma'lumotlar bazasi tayyor: %s", config.DB_PATH)

    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    router = build_router()
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await bot.delete_webhook(drop_pending_updates=True)
    await _start_web_server()

    logger.info("Bot ishga tushmoqda...")
    await asyncio.gather(
        dp.start_polling(bot, owner_id=config.MAIN_OWNER_ID, handle_signals=False),
        scheduler.premium_watcher(bot),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
