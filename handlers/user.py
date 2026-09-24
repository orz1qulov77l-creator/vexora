"""Oddiy foydalanuvchi funksiyalari: /start, kino qidirish, tariflar, hisobim."""
from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

import database as db
import keyboards as kb
from states import SearchMovie
from utils import check_subscription, is_valid_code, render_start_message


# --------------------------------------------------------------- helpers
async def send_main_menu(message: Message, owner_id: int, text: str = "Bosh menyu:") -> None:
    user = db.get_user(owner_id, message.from_user.id)
    tariff = user["tariff"] if user else "STANDARD"
    await message.answer(text, reply_markup=kb.main_menu_kb(tariff))


async def _channels_or_none(owner_id: int, bot: Bot, user_id: int):
    channels = db.list_channels(owner_id)
    if not channels:
        return []
    return await check_subscription(bot, user_id, channels)


# ----------------------------------------------------------------- /start
async def cmd_start(message: Message, state: FSMContext, bot: Bot, owner_id: int) -> None:
    await state.clear()
    user = message.from_user
    db.ensure_user(owner_id, user.id, user.username, user.full_name)

    not_subscribed = await _channels_or_none(owner_id, bot, user.id)
    if not_subscribed:
        text = (
            "⚠️ Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling, "
            "so'ng \u2705 TEKSHIRISH tugmasini bosing:"
        )
        markup = kb.subscribe_kb(
            [dict(id=c["id"], name=c["name"], link=c["link"]) for c in not_subscribed]
        )
        await message.answer(text, reply_markup=markup)
        return

    template = db.get_setting(owner_id, "START_MESSAGE")
    text = render_start_message(template, user.full_name, user.username or "")
    await message.answer(text)

    # Reklama (agar sozlangan bo'lsa)
    await _send_ad_if_any(message, owner_id)

    await send_main_menu(message, owner_id)


async def _send_ad_if_any(message: Message, owner_id: int) -> None:
    ad_type = db.get_setting(owner_id, "AD_TYPE")
    if not ad_type:
        return
    ad_text = db.get_setting(owner_id, "AD_TEXT")
    ad_file = db.get_setting(owner_id, "AD_FILE_ID")
    btn_text = db.get_setting(owner_id, "AD_BUTTON_TEXT")
    btn_url = db.get_setting(owner_id, "AD_BUTTON_URL")

    markup = None
    if btn_text and btn_url:
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

        markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=btn_text, url=btn_url)]]
        )

    try:
        if ad_type == "text" and ad_text:
            await message.answer(ad_text, reply_markup=markup)
        elif ad_type == "photo" and ad_file:
            await message.answer_photo(ad_file, caption=ad_text or None, reply_markup=markup)
        elif ad_type == "audio" and ad_file:
            await message.answer_audio(ad_file, caption=ad_text or None, reply_markup=markup)
    except TelegramBadRequest:
        pass


async def check_sub_callback(callback: CallbackQuery, bot: Bot, owner_id: int) -> None:
    user = callback.from_user
    not_subscribed = await _channels_or_none(owner_id, bot, user.id)
    if not_subscribed:
        await callback.answer("❌ Siz hali barcha kanallarga obuna bo'lmagansiz!", show_alert=True)
        markup = kb.subscribe_kb(
            [dict(id=c["id"], name=c["name"], link=c["link"]) for c in not_subscribed]
        )
        try:
            await callback.message.edit_reply_markup(reply_markup=markup)
        except TelegramBadRequest:
            pass
        return
    await callback.answer("✅ Obuna tasdiqlandi!")
    db.ensure_user(owner_id, user.id, user.username, user.full_name)
    await callback.message.delete()
    await send_main_menu(callback.message, owner_id, "Xush kelibsiz! Bosh menyu:")


# ------------------------------------------------------------ kino qidirish
async def search_button(message: Message, state: FSMContext) -> None:
    await state.set_state(SearchMovie.waiting_code)
    await message.answer(
        "🔎 Qidirmoqchi bo'lgan kinoning kodini kiriting (masalan: 124):",
        reply_markup=kb.cancel_kb(),
    )


async def process_movie_code(message: Message, state: FSMContext, owner_id: int) -> None:
    code = (message.text or "").strip()
    if not is_valid_code(code):
        await message.answer(
            "❗️ Kod noto'g'ri. Kod faqat 2-4 xonali raqamlardan iborat bo'lishi kerak. Qaytadan urinib ko'ring:"
        )
        return

    movie = db.get_movie(owner_id, code)
    if movie is None:
        await message.answer("😔 Bunday kodli kino topilmadi. Boshqa kodni sinab ko'ring.")
        return

    if movie["tariff"] == "PREMIUM":
        user = db.get_user(owner_id, message.from_user.id)
        if not user or user["tariff"] != "PREMIUM":
            await message.answer(
                "⭐ Bu kino faqat PREMIUM foydalanuvchilar uchun.\n"
                "Premium sotib olish uchun \"💳 TARIFLAR\" bo'limiga o'ting."
            )
            await state.clear()
            return

    await state.clear()
    caption = f"🎬 <b>{movie['title']}</b>\n\n{movie['description'] or ''}"
    if movie["poster_file_id"]:
        try:
            await message.answer_photo(movie["poster_file_id"], caption=caption)
        except TelegramBadRequest:
            await message.answer(caption)
        try:
            await message.answer_video(movie["video_file_id"])
        except TelegramBadRequest:
            await message.answer("❗️ Video yuborishda xatolik yuz berdi. Admin bilan bog'laning.")
        return

    try:
        await message.answer_video(movie["video_file_id"], caption=caption)
    except TelegramBadRequest:
        await message.answer(caption)
        try:
            await message.answer_video(movie["video_file_id"])
        except TelegramBadRequest:
            await message.answer("❗️ Video yuborishda xatolik yuz berdi. Admin bilan bog'laning.")


# -------------------------------------------------------------------- cancel
async def cancel_callback(callback: CallbackQuery, state: FSMContext, owner_id: int) -> None:
    await state.clear()
    await callback.answer("Bekor qilindi")
    try:
        await callback.message.delete()
    except TelegramBadRequest:
        pass
    await send_main_menu(callback.message, owner_id)


# ------------------------------------------------------------------ tariflar
async def tariffs_button(message: Message, owner_id: int) -> None:
    price = db.get_setting(owner_id, "PREMIUM_PRICE")
    days = db.get_setting(owner_id, "PREMIUM_DAYS")
    text = (
        "💳 <b>Tariflar</b>\n\n"
        "🆓 <b>STANDARD</b> — bepul, faqat bepul kinolarni tomosha qilish mumkin.\n\n"
        f"⭐ <b>PREMIUM</b> — {price} so'm / {days} kun.\n"
        "— barcha premium kinolarga kirish\n"
    )
    await message.answer(text, reply_markup=kb.tariffs_kb())


async def buy_premium_callback(callback: CallbackQuery, owner_id: int) -> None:
    admin_contact = db.get_setting(owner_id, "ADMIN_CONTACT")
    price = db.get_setting(owner_id, "PREMIUM_PRICE")
    await callback.answer()
    await callback.message.answer(
        f"⭐ PREMIUM narxi: {price} so'm.\n\n"
        f"To'lov faqat admin orqali amalga oshiriladi.\n"
        f"Quyidagi ID'ingizni {admin_contact} ga yuborib, balansingizni to'ldirishni so'rang, "
        f"so'ngra \"💳 TARIFLAR\" orqali premium sotib oling.\n\n"
        f"🆔 Sizning ID: <code>{callback.from_user.id}</code>"
    )


# ------------------------------------------------------------------ hisobim
async def account_button(message: Message, owner_id: int) -> None:
    user = db.get_user(owner_id, message.from_user.id)
    if user is None:
        db.ensure_user(owner_id, message.from_user.id, message.from_user.username, message.from_user.full_name)
        user = db.get_user(owner_id, message.from_user.id)

    premium_line = "—"
    if user["tariff"] == "PREMIUM" and user["premium_until"]:
        premium_line = user["premium_until"]

    text = (
        "👤 <b>Hisobim</b>\n\n"
        f"🆔 ID: <code>{user['user_id']}</code>\n"
        f"💳 Tarif: {user['tariff']}\n"
        f"💰 Balans: {user['balance']} so'm\n"
        f"📅 Ro'yxatdan o'tgan: {user['joined_at']}\n"
        f"⭐ Premium tugash sanasi: {premium_line}\n"
    )

    await message.answer(text, reply_markup=kb.account_kb())


async def topup_info_callback(callback: CallbackQuery, owner_id: int) -> None:
    admin_contact = db.get_setting(owner_id, "ADMIN_CONTACT")
    await callback.answer()
    await callback.message.answer(
        f"💰 Balansni to'ldirish uchun {admin_contact} ga murojaat qiling va quyidagi ID'ingizni yuboring:\n\n"
        f"🆔 <code>{callback.from_user.id}</code>"
    )


# --------------------------------------------------------------- register
def register(router: Router) -> None:
    router.message.register(cmd_start, CommandStart())
    router.callback_query.register(check_sub_callback, F.data == "check_sub")

    router.message.register(search_button, F.text == kb.BTN_SEARCH)
    router.message.register(process_movie_code, SearchMovie.waiting_code)

    router.message.register(tariffs_button, F.text == kb.BTN_TARIFFS)
    router.callback_query.register(buy_premium_callback, F.data == "buy_premium")

    router.message.register(account_button, F.text == kb.BTN_ACCOUNT)
    router.callback_query.register(topup_info_callback, F.data == "topup_info")

    router.callback_query.register(cancel_callback, F.data == "cancel")
