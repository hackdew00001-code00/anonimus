from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

from database.db import (
    add_or_update_user,
    set_user_language,
    get_user_language,
    get_user_stats,
    get_connection_by_user
)
from locales.texts import get_text
from keyboards.inline import (
    get_language_keyboard,
    get_main_menu_keyboard,
    get_back_keyboard
)

router = Router(name="start_router")

async def get_menu_content(user, bot: Bot, lang: str) -> tuple[str, any]:
    """Foydalanuvchining ulanish holatini tekshirib, mos menyuni qaytaradi."""
    bot_info = await bot.get_me()
    conn_id = await get_connection_by_user(user.id)
    is_connected = False

    if conn_id:
        try:
            conn = await bot.get_business_connection(conn_id)
            if conn and conn.is_enabled:
                is_connected = True
        except Exception:
            is_connected = False

    if is_connected:
        text = get_text(
            lang,
            "menu_text_connected",
            name=user.full_name,
            username=f"@{user.username}" if user.username else "Username yo'q"
        )
    else:
        text = get_text(lang, "menu_text_unconnected")

    keyboard = get_main_menu_keyboard(lang, bot_info.username, is_connected=is_connected)
    return text, keyboard

@router.message(CommandStart())
async def start_handler(message: Message, bot: Bot):
    user = message.from_user
    if not user:
        return

    await add_or_update_user(
        user_id=user.id,
        first_name=user.first_name,
        username=user.username
    )

    # Agar foydalanuvchi allaqachon til tanlagan bo'lsa, to'g'ridan-to'g'ri holatini ko'rsatish
    lang = await get_user_language(user.id)
    conn_id = await get_connection_by_user(user.id)

    if conn_id:
        text, keyboard = await get_menu_content(user, bot, lang)
        await message.answer(text=text, reply_markup=keyboard, parse_mode="HTML")
    else:
        await message.answer(
            text=get_text(lang, "welcome"),
            reply_markup=get_language_keyboard(),
            parse_mode="HTML"
        )

@router.callback_query(F.data.startswith("setlang_"))
async def language_selected_handler(callback: CallbackQuery, bot: Bot):
    user = callback.from_user
    lang = callback.data.split("_")[1]

    await set_user_language(user.id, lang)
    text, keyboard = await get_menu_content(user, bot, lang)

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_check_conn")
async def check_connection_handler(callback: CallbackQuery, bot: Bot):
    """Foydalanuvchi ulanishni tekshirish tugmasini bosganda."""
    user = callback.from_user
    lang = await get_user_language(user.id)
    conn_id = await get_connection_by_user(user.id)
    is_connected = False

    if conn_id:
        try:
            conn = await bot.get_business_connection(conn_id)
            if conn and conn.is_enabled:
                is_connected = True
        except Exception:
            is_connected = False

    if is_connected:
        await callback.answer(
            "✅ Botingiz hisobingizga muvaffaqiyatli ulangan va faol!",
            show_alert=True
        )
    else:
        await callback.answer(
            "❌ Bot hali ulanmagan. Iltimos, Telegram Sozlamalar -> Chat-botlar bo'limidan botni qo'shing.",
            show_alert=True
        )

    text, keyboard = await get_menu_content(user, bot, lang)
    try:
        await callback.message.edit_text(text=text, reply_markup=keyboard, parse_mode="HTML")
    except Exception:
        pass

@router.callback_query(F.data == "menu_help")
async def help_callback_handler(callback: CallbackQuery, bot: Bot):
    lang = await get_user_language(callback.from_user.id)
    bot_info = await bot.get_me()

    await callback.message.edit_text(
        text=get_text(lang, "help_text", bot_username=bot_info.username),
        reply_markup=get_back_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_stats")
async def stats_callback_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    lang = await get_user_language(user_id)
    stats = await get_user_stats(user_id)

    text = get_text(
        lang,
        "stats_text",
        photos=stats["photos"],
        videos=stats["videos"],
        total=stats["total"]
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=get_back_keyboard(lang),
        parse_mode="HTML"
    )
    await callback.answer()

@router.callback_query(F.data == "menu_lang")
async def change_lang_callback_handler(callback: CallbackQuery):
    await callback.message.edit_text(
        text="🌐 Tilni tanlang / Выберите язык:",
        reply_markup=get_language_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "menu_back")
async def back_callback_handler(callback: CallbackQuery, bot: Bot):
    user = callback.from_user
    lang = await get_user_language(user.id)
    text, keyboard = await get_menu_content(user, bot, lang)

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()
