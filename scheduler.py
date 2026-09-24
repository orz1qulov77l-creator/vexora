"""Fonda ishlaydigan vazifa:
1) Premium tugashiga 24 soat qolganda foydalanuvchini ogohlantiradi.
2) Premium tugagan foydalanuvchini avtomatik ravishda STANDARD tarifga tushiradi.
"""
import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

import config
import database as db

logger = logging.getLogger("scheduler")

CHECK_INTERVAL_SECONDS = 1800  # 30 daqiqada bir marta tekshiradi


async def _notify(bot: Bot, user_id: int, text: str) -> None:
    try:
        await bot.send_message(user_id, text)
    except (TelegramForbiddenError, TelegramBadRequest):
        pass


async def premium_watcher(bot: Bot) -> None:
    owner_id = config.MAIN_OWNER_ID
    while True:
        try:
            # 24 soat ichida tugaydigan premiumlar haqida ogohlantirish
            for u in db.expiring_premium_users(owner_id, within_hours=24):
                await _notify(
                    bot,
                    u["user_id"],
                    "⚠️ Sizning PREMIUM tarifingiz 24 soatdan so'ng tugaydi. "
                    "Uzaytirish uchun admin bilan bog'laning.",
                )
                db.mark_premium_notified(owner_id, u["user_id"])

            # Muddati tugagan premiumlarni STANDARD ga tushirish
            for u in db.expired_premium_users(owner_id):
                db.set_tariff(owner_id, u["user_id"], "STANDARD", None)
                await _notify(
                    bot,
                    u["user_id"],
                    "ℹ️ PREMIUM muddatingiz tugadi, tarifingiz STANDARD ga o'zgartirildi.",
                )

        except Exception:
            logger.exception("premium_watcher xatolik bilan to'xtamadi, davom etmoqda")

        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
