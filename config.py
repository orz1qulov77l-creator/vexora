"""
Barcha sozlamalar shu yerdan Render.com "Environment" bo'limida
o'rnatiladigan environment variablelar orqali o'qiladi.

MAJBURIY environment variablelar (Render Dashboard -> Environment):
    BOT_TOKEN   - @BotFather dan olingan asosiy bot tokeni
    ADMIN_ID    - Asosiy (ASOSIY ADMIN) foydalanuvchining Telegram ID raqami

IXTIYORIY environment variablelar:
    DB_PATH     - SQLite baza fayli yo'li (standart: kino_bot.db)
    PORT        - Render avtomatik beradi, qo'lda kerak emas
"""
import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID_RAW: str = os.getenv("ADMIN_ID", "0").strip()

try:
    ADMIN_ID: int = int(ADMIN_ID_RAW)
except ValueError:
    ADMIN_ID = 0

DB_PATH: str = os.getenv("DB_PATH", "kino_bot.db")

# Render avtomatik shu portni beradi, lokal test uchun 8081 ishlatiladi
PORT: int = int(os.getenv("PORT", "8081"))

# Bot ma'lumotlar bazasida "asosiy bot" har doim owner_id = 0 bilan belgilanadi.
MAIN_OWNER_ID: int = 0

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN environment o'zgaruvchisi topilmadi. "
        "Render -> Environment bo'limiga BOT_TOKEN qo'shing."
    )

if ADMIN_ID == 0:
    raise RuntimeError(
        "ADMIN_ID environment o'zgaruvchisi topilmadi yoki noto'g'ri. "
        "Render -> Environment bo'limiga ADMIN_ID (sizning Telegram ID) qo'shing."
    )
