"""Yordamchi funksiyalar: obuna tekshirish, formatlash, validatsiya."""
import re

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

import database as db

SUBSCRIBED_STATUSES = {"member", "administrator", "creator"}

CODE_RE = re.compile(r"^\d{2,4}$")


def is_valid_code(code: str) -> bool:
    """Kino kodi: faqat 2-4 xonali raqam, harflar bo'lmasligi kerak."""
    return bool(CODE_RE.match(code.strip()))


def channel_ref_from_link(link: str) -> str:
    """Admin kiritgan linkdan (https://t.me/username yoki @username yoki
    oddiy username) Bot API uchun ishlatsa bo'ladigan '@username' ko'rinishini
    chiqarib beradi. Xususiy (+hash) linklarni aniqlab, alohida belgi qaytaradi."""
    link = link.strip()
    if "t.me/+" in link or "joinchat" in link:
        # Xususiy taklif linki - Bot API orqali a'zolikni to'g'ridan-to'g'ri
        # tekshirib bo'lmaydi (botga faqat kanal ID kerak). Shu holatda
        # linkni o'zgarishsiz saqlaymiz, admin botni kanalga admin qilib
        # qo'shgan bo'lishi va kerak bo'lsa keyinchalik chat_id bilan
        # yangilashi kerak.
        return link
    match = re.search(r"t\.me/([A-Za-z0-9_]+)", link)
    if match:
        return "@" + match.group(1)
    if link.startswith("@"):
        return link
    return "@" + link.lstrip("@")


async def check_subscription(bot: Bot, user_id: int, channels: list) -> list:
    """Barcha majburiy kanallarga obuna bo'lmagan kanallar ro'yxatini qaytaradi.
    Bo'sh ro'yxat = foydalanuvchi barcha kanallarga obuna."""
    not_subscribed = []
    for ch in channels:
        chat_ref = ch["chat_ref"]
        if chat_ref.startswith("t.me/+") or "joinchat" in chat_ref:
            # Xususiy taklif linki - tekshira olmaymiz, o'tkazib yuboramiz
            continue
        try:
            member = await bot.get_chat_member(chat_id=chat_ref, user_id=user_id)
            if member.status not in SUBSCRIBED_STATUSES:
                not_subscribed.append(ch)
        except (TelegramBadRequest, TelegramForbiddenError):
            # Bot kanalda admin emas yoki kanal topilmadi - xavfsizlik uchun
            # obuna bo'lmagan deb hisoblaymiz va adminlarga muammoni bildirish
            # uchun ro'yxatga qo'shamiz
            not_subscribed.append(ch)
    return not_subscribed


def render_start_message(template: str, full_name: str, username: str) -> str:
    """Start xabaridagi '()' belgisini foydalanuvchi nomi bilan almashtiradi."""
    mention = f"@{username}" if username else full_name
    if "()" in template:
        return template.replace("()", mention)
    return template


def format_user_row(u) -> str:
    username = f"@{u['username']}" if u["username"] else "—"
    return (
        f"🆔 ID: <code>{u['user_id']}</code>\n"
        f"👤 Ism: {u['full_name'] or '—'}\n"
        f"🔗 Username: {username}\n"
        f"💳 Tarif: {u['tariff']}\n"
        f"💰 Balans: {u['balance']} so'm\n"
    )


def format_admin_row(a) -> str:
    user = db.get_user(a["owner_id"], a["user_id"])
    balance = user["balance"] if user else 0
    username = f"@{user['username']}" if user and user["username"] else "—"
    name = user["full_name"] if user else "—"
    return (
        f"🆔 ID: <code>{a['user_id']}</code>\n"
        f"👤 Ism: {name}\n"
        f"🔗 Username: {username}\n"
        f"🎖 Daraja: {a['level']}\n"
        f"💰 Balans: {balance} so'm\n"
    )

