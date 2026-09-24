"""Barcha reply va inline klaviaturalar shu yerda."""
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

# ------------------------------------------------------------ USER MENU
BTN_SEARCH = "🎬 KINO QIDIRISH"
BTN_TARIFFS = "💳 TARIFLAR"
BTN_ACCOUNT = "👤 HISOBIM"


def main_menu_kb(tariff: str) -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text=BTN_SEARCH))
    builder.row(KeyboardButton(text=BTN_TARIFFS), KeyboardButton(text=BTN_ACCOUNT))
    return builder.as_markup(resize_keyboard=True)


def subscribe_kb(channels: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.row(InlineKeyboardButton(text=ch["name"], url=ch["link"]))
    builder.row(InlineKeyboardButton(text="✅ TEKSHIRISH", callback_data="check_sub"))
    return builder.as_markup()


def tariffs_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⭐ PREMIUM SOTIB OLISH", callback_data="buy_premium"))
    return builder.as_markup()


def account_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💰 BALANSNI TO'LDIRISH", callback_data="topup_info"))
    return builder.as_markup()


def confirm_cancel_kb(confirm_cb: str, cancel_cb: str = "cancel") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=confirm_cb),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data=cancel_cb),
    )
    return builder.as_markup()


def cancel_kb(cancel_cb: str = "cancel") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data=cancel_cb))
    return builder.as_markup()


def tariff_choice_kb(prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="STANDARD", callback_data=f"{prefix}:STANDARD"),
        InlineKeyboardButton(text="PREMIUM", callback_data=f"{prefix}:PREMIUM"),
    )
    return builder.as_markup()


# ----------------------------------------------------------- ADMIN MENU
ADMIN_MENU_ITEMS = [
    ("🎬 Kino qo'shish", "adm:add_movie"),
    ("✏️ Kino tahrirlash", "adm:edit_movie"),
    ("💰 Balans to'ldirish", "adm:topup"),
    ("⭐ Premium berish", "adm:give_premium"),
    ("💵 Narxlarni belgilash", "adm:prices"),
    ("📢 Majburiy kanal qo'shish", "adm:add_channel"),
    ("📝 Majburiy kanallarni tahrirlash", "adm:edit_channel"),
    ("📊 Statistika", "adm:stats"),
    ("👮 Admin qo'shish", "adm:add_admin"),
    ("🛠 Admin tahrirlash", "adm:edit_admin"),
    ("📣 Ommaviy xabar", "adm:broadcast"),
    ("🖼 Reklama", "adm:ads"),
    ("🔤 Matn/username tahrirlash", "adm:edit_texts"),
    ("💬 Start xabarini tahrirlash", "adm:edit_start"),
]


def admin_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for text, cb in ADMIN_MENU_ITEMS:
        builder.row(InlineKeyboardButton(text=text, callback_data=cb))
    return builder.as_markup()


def back_to_admin_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Admin menyu", callback_data="adm:menu"))
    return builder.as_markup()


def movie_edit_fields_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    fields = [
        ("Kodini o'zgartirish", "code"),
        ("Nomini o'zgartirish", "title"),
        ("Tavsifini o'zgartirish", "description"),
        ("Videosini o'zgartirish", "video_file_id"),
        ("Bannerini o'zgartirish", "poster_file_id"),
        ("Tarifini o'zgartirish", "tariff"),
        ("🗑 O'chirish", "delete"),
    ]
    for text, field in fields:
        builder.row(InlineKeyboardButton(text=text, callback_data=f"editmv:{field}"))
    builder.row(InlineKeyboardButton(text="⬅️ Admin menyu", callback_data="adm:menu"))
    return builder.as_markup()


def channels_list_kb(channels: list, prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.row(InlineKeyboardButton(text=ch["name"], callback_data=f"{prefix}:{ch['id']}"))
    builder.row(InlineKeyboardButton(text="⬅️ Admin menyu", callback_data="adm:menu"))
    return builder.as_markup()


def channel_edit_fields_kb(channel_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Nomini o'zgartirish", callback_data=f"editch:name:{channel_id}"))
    builder.row(InlineKeyboardButton(text="Linkini o'zgartirish", callback_data=f"editch:link:{channel_id}"))
    builder.row(InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"editch:delete:{channel_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Admin menyu", callback_data="adm:menu"))
    return builder.as_markup()


def stats_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    items = [
        ("👥 Barcha foydalanuvchilar", "stats:all"),
        ("⭐ Premium foydalanuvchilar", "stats:premium"),
        ("🆓 Standard foydalanuvchilar", "stats:standard"),
        ("📢 Majburiy kanallar", "stats:channels"),
        ("🏆 TOP-15 to'ldiruvchi", "stats:top15"),
        ("👮 Adminlar", "stats:admins"),
    ]
    for text, cb in items:
        builder.row(InlineKeyboardButton(text=text, callback_data=cb))
    builder.row(InlineKeyboardButton(text="⬅️ Admin menyu", callback_data="adm:menu"))
    return builder.as_markup()


def admin_level_kb(prefix: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for level in ("ASOSIY", "SUB-ADMIN", "ODDIY"):
        builder.row(InlineKeyboardButton(text=level, callback_data=f"{prefix}:{level}"))
    return builder.as_markup()


def admins_list_kb(admins: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for a in admins:
        label = f"{a['user_id']} ({a['level']})"
        builder.row(InlineKeyboardButton(text=label, callback_data=f"editadm:{a['user_id']}"))
    builder.row(InlineKeyboardButton(text="⬅️ Admin menyu", callback_data="adm:menu"))
    return builder.as_markup()


def edit_admin_actions_kb(user_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Darajasini o'zgartirish", callback_data=f"admact:level:{user_id}"))
    builder.row(InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"admact:delete:{user_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Admin menyu", callback_data="adm:menu"))
    return builder.as_markup()


def broadcast_audience_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⭐ Faqat PREMIUM", callback_data="bcast_aud:PREMIUM"))
    builder.row(InlineKeyboardButton(text="🆓 Faqat STANDARD", callback_data="bcast_aud:STANDARD"))
    builder.row(InlineKeyboardButton(text="👥 HAMMASI", callback_data="bcast_aud:ALL"))
    return builder.as_markup()


def ad_type_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📝 Matn", callback_data="adtype:text"))
    builder.row(InlineKeyboardButton(text="🖼 Rasm", callback_data="adtype:photo"))
    builder.row(InlineKeyboardButton(text="🎵 Audio", callback_data="adtype:audio"))
    builder.row(InlineKeyboardButton(text="🚫 O'chirish", callback_data="adtype:none"))
    return builder.as_markup()


def edit_texts_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Admin username (@kontakt)", callback_data="edittxt:ADMIN_CONTACT"))
    builder.row(InlineKeyboardButton(text="⬅️ Admin menyu", callback_data="adm:menu"))
    return builder.as_markup()


def prices_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="PREMIUM narxi", callback_data="price:PREMIUM_PRICE"))
    builder.row(InlineKeyboardButton(text="PREMIUM muddati (kun)", callback_data="price:PREMIUM_DAYS"))
    builder.row(InlineKeyboardButton(text="⬅️ Admin menyu", callback_data="adm:menu"))
    return builder.as_markup()
