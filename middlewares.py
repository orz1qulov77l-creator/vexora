"""Majburiy obuna middleware - har bir xabar/callback uchun tekshiradi.

/start buyrug'i va 'check_sub' callback'i bundan mustasno - ular o'z
ichida obunani alohida tekshiradi (chunki hali foydalanuvchi ro'yxatdan
o'tmagan yoki aynan tekshirish tugmasini bosgan bo'ladi).

Admin foydalanuvchilar majburiy obunadan ozod qilingan (o'zi test qilishi
va boshqarishi qulay bo'lishi uchun).
"""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware, Bot
from aiogram.types import CallbackQuery, Message, TelegramObject

import database as db
import keyboards as kb
from utils import check_subscription

EXEMPT_CALLBACKS = {"check_sub"}


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        owner_id = data.get("owner_id", 0)
        bot: Bot = data.get("bot")

        user_id = None
        if isinstance(event, Message):
            if event.text == "/start":
                return await handler(event, data)
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            if event.data in EXEMPT_CALLBACKS:
                return await handler(event, data)
            user_id = event.from_user.id

        if user_id is None:
            return await handler(event, data)

        if db.is_admin(owner_id, user_id) is not None:
            return await handler(event, data)

        channels = db.list_channels(owner_id)
        if channels:
            not_subscribed = await check_subscription(bot, user_id, channels)
            if not_subscribed:
                text = (
                    "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling, "
                    "so'ng \u2705 TEKSHIRISH tugmasini bosing:"
                )
                markup = kb.subscribe_kb(
                    [dict(id=c["id"], name=c["name"], link=c["link"]) for c in not_subscribed]
                )
                if isinstance(event, Message):
                    await event.answer(text, reply_markup=markup)
                else:
                    await event.answer()
                    try:
                        await event.message.answer(text, reply_markup=markup)
                    except Exception:
                        pass
                return None

        return await handler(event, data)
