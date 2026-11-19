from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from locales.texts import get_text

def get_language_keyboard() -> InlineKeyboardMarkup:
    """Tilni tanlash tugmalari."""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="setlang_uz"),
                InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang_ru")
            ]
        ]
    )
    return keyboard

def get_main_menu_keyboard(lang: str, bot_username: str, is_connected: bool = False) -> InlineKeyboardMarkup:
    """Asosiy menyu tugmalari (ulangan yoki ulanmagan holatiga qarab)."""
    help_btn_text = get_text(lang, "btn_help")
    stats_btn_text = get_text(lang, "btn_stats")
    lang_btn_text = get_text(lang, "btn_lang")
    check_btn_text = get_text(lang, "btn_check")

    if is_connected:
        # Bot allaqachon ulangan bo'lsa: "Botni ulash" tugmasi yo'qoladi!
        status_text = get_text(lang, "btn_status_connected")
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=status_text, callback_data="menu_check_conn")
                ],
                [
                    InlineKeyboardButton(text=stats_btn_text, callback_data="menu_stats"),
                    InlineKeyboardButton(text=check_btn_text, callback_data="menu_check_conn")
                ],
                [
                    InlineKeyboardButton(text=help_btn_text, callback_data="menu_help"),
                    InlineKeyboardButton(text=lang_btn_text, callback_data="menu_lang")
                ]
            ]
        )
    else:
        # Hali ulanmagan bo'lsa: Botni ulash tugmasi ko'rsatiladi
        connect_btn_text = get_text(lang, "btn_connect")
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text=connect_btn_text, url="tg://settings/business_chatbots")
                ],
                [
                    InlineKeyboardButton(text=check_btn_text, callback_data="menu_check_conn"),
                    InlineKeyboardButton(text=stats_btn_text, callback_data="menu_stats")
                ],
                [
                    InlineKeyboardButton(text=help_btn_text, callback_data="menu_help"),
                    InlineKeyboardButton(text=lang_btn_text, callback_data="menu_lang")
                ]
            ]
        )

    return keyboard

def get_back_keyboard(lang: str) -> InlineKeyboardMarkup:
    """Orqaga qaytish tugmasi."""
    text = "🔙 Orqaga" if lang == "uz" else "🔙 Назад"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text, callback_data="menu_back")]
        ]
    )
