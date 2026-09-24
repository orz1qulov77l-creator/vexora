"""
Ma'lumotlar bazasi qatlami (SQLite, standart kutubxona - qo'shimcha
kutubxona shart emas, shuning uchun Render'da "kutubxona topilmadi"
degan xato chiqishi mumkin emas).

Izoh - "owner_id":
    Har bir jadvalda owner_id ustuni bor, u har doim 0 qiymatida bo'ladi
    (bitta bot uchun ichki texnik maydon, boshqa hech narsaga ta'sir
    qilmaydi).
"""
import sqlite3
import time
from typing import Any, Optional

import config

_conn: Optional[sqlite3.Connection] = None


def get_conn() -> sqlite3.Connection:
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA journal_mode=WAL;")
        _conn.execute("PRAGMA foreign_keys=ON;")
    return _conn


def now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id         INTEGER NOT NULL,
            owner_id        INTEGER NOT NULL DEFAULT 0,
            username        TEXT,
            full_name       TEXT,
            tariff          TEXT NOT NULL DEFAULT 'STANDARD',
            balance         INTEGER NOT NULL DEFAULT 0,
            premium_until   TEXT,
            premium_notified INTEGER NOT NULL DEFAULT 0,
            total_topup     INTEGER NOT NULL DEFAULT 0,
            joined_at       TEXT,
            referred_by     INTEGER,
            PRIMARY KEY (user_id, owner_id)
        );

        CREATE TABLE IF NOT EXISTS movies (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id        INTEGER NOT NULL DEFAULT 0,
            code            TEXT NOT NULL,
            title           TEXT NOT NULL,
            description     TEXT,
            video_file_id   TEXT NOT NULL,
            poster_file_id  TEXT,
            tariff          TEXT NOT NULL DEFAULT 'STANDARD',
            created_at      TEXT,
            UNIQUE(owner_id, code)
        );

        CREATE TABLE IF NOT EXISTS channels (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id    INTEGER NOT NULL DEFAULT 0,
            name        TEXT NOT NULL,
            link        TEXT NOT NULL,
            chat_ref    TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS admins (
            user_id             INTEGER NOT NULL,
            owner_id            INTEGER NOT NULL DEFAULT 0,
            level               TEXT NOT NULL DEFAULT 'ODDIY',
            can_manage_admins   INTEGER NOT NULL DEFAULT 0,
            added_at            TEXT,
            PRIMARY KEY (user_id, owner_id)
        );

        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            owner_id    INTEGER NOT NULL DEFAULT 0,
            amount      INTEGER NOT NULL,
            ttype       TEXT NOT NULL,
            note        TEXT,
            created_at  TEXT
        );

        CREATE TABLE IF NOT EXISTS settings (
            owner_id    INTEGER NOT NULL DEFAULT 0,
            key         TEXT NOT NULL,
            value       TEXT,
            PRIMARY KEY (owner_id, key)
        );
        """
    )
    conn.commit()

    _seed_default_settings(config.MAIN_OWNER_ID)

    # Asosiy admin har doim admins jadvalida ASOSIY daraja bilan bo'lishi kerak
    cur.execute(
        "SELECT 1 FROM admins WHERE user_id=? AND owner_id=?",
        (config.ADMIN_ID, config.MAIN_OWNER_ID),
    )
    if cur.fetchone() is None:
        cur.execute(
            "INSERT INTO admins (user_id, owner_id, level, can_manage_admins, added_at) "
            "VALUES (?, ?, 'ASOSIY', 1, ?)",
            (config.ADMIN_ID, config.MAIN_OWNER_ID, now()),
        )
        conn.commit()


DEFAULT_SETTINGS = {
    "PREMIUM_PRICE": "25000",
    "PREMIUM_DAYS": "30",
    "START_MESSAGE": "Salom, ()! Kino botimizga xush kelibsiz.",
    "ADMIN_CONTACT": "@admin",
    "AD_TYPE": "",
    "AD_TEXT": "",
    "AD_FILE_ID": "",
    "AD_BUTTON_TEXT": "",
    "AD_BUTTON_URL": "",
}


def _seed_default_settings(owner_id: int) -> None:
    conn = get_conn()
    cur = conn.cursor()
    for key, value in DEFAULT_SETTINGS.items():
        cur.execute(
            "INSERT OR IGNORE INTO settings (owner_id, key, value) VALUES (?, ?, ?)",
            (owner_id, key, value),
        )
    conn.commit()


# ---------------------------------------------------------------- SETTINGS
def get_setting(owner_id: int, key: str, default: str = "") -> str:
    conn = get_conn()
    row = conn.execute(
        "SELECT value FROM settings WHERE owner_id=? AND key=?", (owner_id, key)
    ).fetchone()
    if row is None or row["value"] is None:
        return DEFAULT_SETTINGS.get(key, default)
    return row["value"]


def set_setting(owner_id: int, key: str, value: str) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO settings (owner_id, key, value) VALUES (?, ?, ?) "
        "ON CONFLICT(owner_id, key) DO UPDATE SET value=excluded.value",
        (owner_id, key, value),
    )
    conn.commit()


# ------------------------------------------------------------------ USERS
def get_user(owner_id: int, user_id: int) -> Optional[sqlite3.Row]:
    conn = get_conn()
    return conn.execute(
        "SELECT * FROM users WHERE owner_id=? AND user_id=?", (owner_id, user_id)
    ).fetchone()


def ensure_user(
    owner_id: int,
    user_id: int,
    username: Optional[str],
    full_name: Optional[str],
    referred_by: Optional[int] = None,
) -> sqlite3.Row:
    conn = get_conn()
    user = get_user(owner_id, user_id)
    if user is None:
        conn.execute(
            "INSERT INTO users (user_id, owner_id, username, full_name, tariff, "
            "balance, joined_at, referred_by) VALUES (?, ?, ?, ?, 'STANDARD', 0, ?, ?)",
            (user_id, owner_id, username, full_name, now(), referred_by),
        )
        conn.commit()
        user = get_user(owner_id, user_id)
    else:
        conn.execute(
            "UPDATE users SET username=?, full_name=? WHERE owner_id=? AND user_id=?",
            (username, full_name, owner_id, user_id),
        )
        conn.commit()
    return user


def list_users(owner_id: int, tariff: Optional[str] = None) -> list:
    conn = get_conn()
    if tariff:
        return conn.execute(
            "SELECT * FROM users WHERE owner_id=? AND tariff=? ORDER BY joined_at DESC",
            (owner_id, tariff),
        ).fetchall()
    return conn.execute(
        "SELECT * FROM users WHERE owner_id=? ORDER BY joined_at DESC", (owner_id,)
    ).fetchall()


def count_users(owner_id: int, tariff: Optional[str] = None) -> int:
    conn = get_conn()
    if tariff:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM users WHERE owner_id=? AND tariff=?",
            (owner_id, tariff),
        ).fetchone()
    else:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM users WHERE owner_id=?", (owner_id,)
        ).fetchone()
    return row["c"] if row else 0


def top_topup_users(owner_id: int, limit: int = 15) -> list:
    conn = get_conn()
    return conn.execute(
        "SELECT * FROM users WHERE owner_id=? AND total_topup>0 "
        "ORDER BY total_topup DESC LIMIT ?",
        (owner_id, limit),
    ).fetchall()


def add_balance(owner_id: int, user_id: int, amount: int, count_as_topup: bool = True) -> None:
    conn = get_conn()
    if count_as_topup:
        conn.execute(
            "UPDATE users SET balance = balance + ?, total_topup = total_topup + ? "
            "WHERE owner_id=? AND user_id=?",
            (amount, amount, owner_id, user_id),
        )
    else:
        conn.execute(
            "UPDATE users SET balance = balance + ? WHERE owner_id=? AND user_id=?",
            (amount, owner_id, user_id),
        )
    conn.commit()


def deduct_balance(owner_id: int, user_id: int, amount: int) -> bool:
    conn = get_conn()
    user = get_user(owner_id, user_id)
    if user is None or user["balance"] < amount:
        return False
    conn.execute(
        "UPDATE users SET balance = balance - ? WHERE owner_id=? AND user_id=?",
        (amount, owner_id, user_id),
    )
    conn.commit()
    return True


def set_tariff(owner_id: int, user_id: int, tariff: str, premium_until: Optional[str] = None) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE users SET tariff=?, premium_until=?, premium_notified=0 "
        "WHERE owner_id=? AND user_id=?",
        (tariff, premium_until, owner_id, user_id),
    )
    conn.commit()


def mark_premium_notified(owner_id: int, user_id: int) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE users SET premium_notified=1 WHERE owner_id=? AND user_id=?",
        (owner_id, user_id),
    )
    conn.commit()


def expiring_premium_users(owner_id: int, within_hours: int = 24) -> list:
    """premium_until vaqti hozirdan `within_hours` soat ichida tugaydigan va
    hali ogohlantirilmagan foydalanuvchilar."""
    conn = get_conn()
    return conn.execute(
        "SELECT * FROM users WHERE owner_id=? AND tariff='PREMIUM' "
        "AND premium_notified=0 AND premium_until IS NOT NULL "
        "AND datetime(premium_until) <= datetime('now', ?) "
        "AND datetime(premium_until) > datetime('now')",
        (owner_id, f"+{within_hours} hours"),
    ).fetchall()


def expired_premium_users(owner_id: int) -> list:
    conn = get_conn()
    return conn.execute(
        "SELECT * FROM users WHERE owner_id=? AND tariff='PREMIUM' "
        "AND premium_until IS NOT NULL AND datetime(premium_until) <= datetime('now')",
        (owner_id,),
    ).fetchall()


# ----------------------------------------------------------------- MOVIES
def add_movie(
    owner_id: int,
    code: str,
    title: str,
    description: str,
    video_file_id: str,
    poster_file_id: Optional[str],
    tariff: str,
) -> bool:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO movies (owner_id, code, title, description, video_file_id, "
            "poster_file_id, tariff, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (owner_id, code, title, description, video_file_id, poster_file_id, tariff, now()),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def get_movie(owner_id: int, code: str) -> Optional[sqlite3.Row]:
    conn = get_conn()
    return conn.execute(
        "SELECT * FROM movies WHERE owner_id=? AND code=?", (owner_id, code)
    ).fetchone()


def update_movie_field(owner_id: int, code: str, field: str, value: Any) -> None:
    allowed = {"code", "title", "description", "video_file_id", "poster_file_id", "tariff"}
    if field not in allowed:
        raise ValueError("Ruxsat etilmagan maydon: %s" % field)
    conn = get_conn()
    conn.execute(
        f"UPDATE movies SET {field}=? WHERE owner_id=? AND code=?",
        (value, owner_id, code),
    )
    conn.commit()


def delete_movie(owner_id: int, code: str) -> None:
    conn = get_conn()
    conn.execute("DELETE FROM movies WHERE owner_id=? AND code=?", (owner_id, code))
    conn.commit()


def count_movies(owner_id: int) -> int:
    conn = get_conn()
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM movies WHERE owner_id=?", (owner_id,)
    ).fetchone()
    return row["c"] if row else 0


# --------------------------------------------------------------- CHANNELS
def add_channel(owner_id: int, name: str, link: str, chat_ref: str) -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO channels (owner_id, name, link, chat_ref) VALUES (?, ?, ?, ?)",
        (owner_id, name, link, chat_ref),
    )
    conn.commit()
    return cur.lastrowid


def list_channels(owner_id: int) -> list:
    conn = get_conn()
    return conn.execute(
        "SELECT * FROM channels WHERE owner_id=? ORDER BY id", (owner_id,)
    ).fetchall()


def get_channel(channel_id: int) -> Optional[sqlite3.Row]:
    conn = get_conn()
    return conn.execute("SELECT * FROM channels WHERE id=?", (channel_id,)).fetchone()


def update_channel_field(channel_id: int, field: str, value: str) -> None:
    allowed = {"name", "link", "chat_ref"}
    if field not in allowed:
        raise ValueError("Ruxsat etilmagan maydon: %s" % field)
    conn = get_conn()
    conn.execute(f"UPDATE channels SET {field}=? WHERE id=?", (value, channel_id))
    conn.commit()


def delete_channel(channel_id: int) -> None:
    conn = get_conn()
    conn.execute("DELETE FROM channels WHERE id=?", (channel_id,))
    conn.commit()


# ----------------------------------------------------------------- ADMINS
def get_admin(owner_id: int, user_id: int) -> Optional[sqlite3.Row]:
    conn = get_conn()
    return conn.execute(
        "SELECT * FROM admins WHERE owner_id=? AND user_id=?", (owner_id, user_id)
    ).fetchone()


def is_admin(owner_id: int, user_id: int) -> Optional[str]:
    row = get_admin(owner_id, user_id)
    return row["level"] if row else None


def list_admins(owner_id: int) -> list:
    conn = get_conn()
    return conn.execute(
        "SELECT * FROM admins WHERE owner_id=? ORDER BY added_at", (owner_id,)
    ).fetchall()


def add_admin(owner_id: int, user_id: int, level: str = "ODDIY", can_manage_admins: bool = False) -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO admins (user_id, owner_id, level, can_manage_admins, added_at) "
        "VALUES (?, ?, ?, ?, ?) ON CONFLICT(user_id, owner_id) DO UPDATE SET "
        "level=excluded.level, can_manage_admins=excluded.can_manage_admins",
        (user_id, owner_id, level, int(can_manage_admins), now()),
    )
    conn.commit()


def update_admin_level(owner_id: int, user_id: int, level: str) -> None:
    conn = get_conn()
    can_manage = 1 if level in ("ASOSIY", "SUB-ADMIN") else 0
    conn.execute(
        "UPDATE admins SET level=?, can_manage_admins=? WHERE owner_id=? AND user_id=?",
        (level, can_manage, owner_id, user_id),
    )
    conn.commit()


def delete_admin(owner_id: int, user_id: int) -> None:
    conn = get_conn()
    conn.execute("DELETE FROM admins WHERE owner_id=? AND user_id=?", (owner_id, user_id))
    conn.commit()


# ------------------------------------------------------------ TRANSACTIONS
def add_transaction(user_id: int, owner_id: int, amount: int, ttype: str, note: str = "") -> None:
    conn = get_conn()
    conn.execute(
        "INSERT INTO transactions (user_id, owner_id, amount, ttype, note, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (user_id, owner_id, amount, ttype, note, now()),
    )
    conn.commit()
