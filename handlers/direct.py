from aiogram import Router, F
from aiogram.types import Message
from database.db import get_user_language

router = Router(name="direct_router")

@router.message(F.photo)
async def direct_photo_handler(message: Message):
    lang = await get_user_language(message.from_user.id)
    text = "✅ <b>Rasm qabul qilindi va bot xotirasiga saqlandi!</b>" if lang == "uz" else "✅ <b>Фото получено и сохранено в памяти бота!</b>"
    await message.reply(text, parse_mode="HTML")

@router.message(F.video | F.video_note)
async def direct_video_handler(message: Message):
    lang = await get_user_language(message.from_user.id)
    text = "✅ <b>Video qabul qilindi va bot xotirasiga saqlandi!</b>" if lang == "uz" else "✅ <b>Видео получено и сохранено в памяти бота!</b>"
    await message.reply(text, parse_mode="HTML")
