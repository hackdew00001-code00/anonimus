import logging
from datetime import datetime
from aiogram import Router, Bot
from aiogram.types import Message, BusinessConnection, BusinessMessagesDeleted

from database.db import (
    save_business_connection,
    get_user_by_connection,
    save_media_record,
    get_media_record,
    get_user_language
)
from locales.texts import get_text

logger = logging.getLogger("TeleKoz.Business")
router = Router(name="business_router")

async def resolve_owner_id(connection_id: str, bot: Bot) -> int | None:
    """Connection ID bo'yicha bot egasini topish (bazadan yoki to'g'ridan-to'g'ri Telegram API dan)."""
    owner_id = await get_user_by_connection(connection_id)
    if not owner_id:
        try:
            conn = await bot.get_business_connection(connection_id)
            if conn and conn.is_enabled:
                owner_id = conn.user.id
                await save_business_connection(connection_id, owner_id, True)
                logger.info(f"Connection Telegram API orqali tiklandi va saqlandi: User {owner_id}")
        except Exception as e:
            logger.error(f"Telegram API dan connection olishda xatolik: {e}")
    return owner_id

@router.business_connection()
async def business_connection_handler(event: BusinessConnection, bot: Bot):
    """Foydalanuvchi botni o'z akkauntiga ulab olganida yoki uzganida ishga tushadi."""
    user_id = event.user.id
    is_enabled = event.is_enabled
    connection_id = event.id

    await save_business_connection(connection_id, user_id, is_enabled)
    lang = await get_user_language(user_id)

    if is_enabled:
        logger.info(f"Yangi akkaunt ulandi: User ID: {user_id}, Connection: {connection_id}")
        await bot.send_message(
            chat_id=user_id,
            text=get_text(lang, "connected_success"),
            parse_mode="HTML"
        )
    else:
        logger.info(f"Akkaunt uzildi: User ID: {user_id}, Connection: {connection_id}")
        await bot.send_message(
            chat_id=user_id,
            text=get_text(lang, "disconnected"),
            parse_mode="HTML"
        )

@router.business_message()
async def business_message_handler(message: Message, bot: Bot):
    """
    Shaxsiy chatlarga kelgan va yuborilgan barcha foto va videolarni ushlab qolish.
    (O'zingiz sinov uchun yuborgan bo'lsangiz ham, suhbatdosh yuborgan bo'lsa ham saqlaydi!)
    """
    try:
        connection_id = message.business_connection_id
        if not connection_id:
            return

        logger.info(
            f"Business xabar: MsgID={message.message_id}, ChatID={message.chat.id}, "
            f"Type={message.content_type}, Photo={bool(message.photo)}, "
            f"Video={bool(message.video)}, Doc={bool(message.document)}, "
            f"Text='{message.text}', Caption='{message.caption}'"
        )

        owner_id = await resolve_owner_id(connection_id, bot)
        if not owner_id:
            logger.warning(f"Connection {connection_id} uchun foydalanuvchi topilmadi.")
            return

        sender = message.from_user
        is_self = bool(sender and sender.id == owner_id)

        if is_self:
            sender_name = f"Siz ({sender.full_name})"
            sender_username = f"@{sender.username}" if sender and sender.username else "Siz"
            prefix = "📤 <b>Siz yuborgan media saqlandi:</b>"
        else:
            sender_name = sender.full_name if sender else "Suhbatdosh"
            sender_username = f"@{sender.username}" if sender and sender.username else "Username yo'q"
            prefix = "📥 <b>Suhbatdosh yuborgan media saqlandi:</b>"

        sender_id = sender.id if sender else 0
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Rasm (shu jumladan bir martalik va vaqtli rasmlar)
        if message.photo:
            photo = message.photo[-1]
            caption = (
                f"{prefix}\n\n"
                f"👤 <b>Kimdan:</b> {sender_name} ({sender_username})\n"
                f"🆔 <b>ID:</b> <code>{sender_id}</code>\n"
                f"📅 <b>Vaqt:</b> {now_str}"
            )
            if message.caption:
                caption += f"\n📝 <b>Izoh:</b> {message.caption}"

            await bot.send_photo(
                chat_id=owner_id,
                photo=photo.file_id,
                caption=caption,
                parse_mode="HTML"
            )

            await save_media_record(
                user_id=owner_id,
                connection_id=connection_id,
                chat_id=message.chat.id,
                message_id=message.message_id,
                sender_name=sender_name,
                sender_username=sender_username,
                media_type="photo",
                file_id=photo.file_id,
                caption=message.caption
            )
            logger.info(f"Rasm muvaffaqiyatli saqlandi va yuborildi: {owner_id}")

        # 2. Video yoki dumaloq video
        elif message.video or message.video_note:
            video_file_id = message.video.file_id if message.video else message.video_note.file_id
            caption = (
                f"{prefix}\n\n"
                f"👤 <b>Kimdan:</b> {sender_name} ({sender_username})\n"
                f"🆔 <b>ID:</b> <code>{sender_id}</code>\n"
                f"📅 <b>Vaqt:</b> {now_str}"
            )
            if message.caption:
                caption += f"\n📝 <b>Izoh:</b> {message.caption}"

            await bot.send_video(
                chat_id=owner_id,
                video=video_file_id,
                caption=caption,
                parse_mode="HTML"
            )

            await save_media_record(
                user_id=owner_id,
                connection_id=connection_id,
                chat_id=message.chat.id,
                message_id=message.message_id,
                sender_name=sender_name,
                sender_username=sender_username,
                media_type="video",
                file_id=video_file_id,
                caption=message.caption
            )
            logger.info(f"Video muvaffaqiyatli saqlandi va yuborildi: {owner_id}")

        # 3. Fayl ko'rinishida yuborilgan rasm yoki video (document)
        elif message.document:
            mime = (message.document.mime_type or "").lower()
            if mime.startswith("image/") or mime.startswith("video/"):
                caption = (
                    f"{prefix} (Fayl ko'rinishida)\n\n"
                    f"👤 <b>Kimdan:</b> {sender_name} ({sender_username})\n"
                    f"🆔 <b>ID:</b> <code>{sender_id}</code>\n"
                    f"📅 <b>Vaqt:</b> {now_str}"
                )
                if message.caption:
                    caption += f"\n📝 <b>Izoh:</b> {message.caption}"

                await bot.send_document(
                    chat_id=owner_id,
                    document=message.document.file_id,
                    caption=caption,
                    parse_mode="HTML"
                )

                await save_media_record(
                    user_id=owner_id,
                    connection_id=connection_id,
                    chat_id=message.chat.id,
                    message_id=message.message_id,
                    sender_name=sender_name,
                    sender_username=sender_username,
                    media_type="document",
                    file_id=message.document.file_id,
                    caption=message.caption
                )
                logger.info(f"Document media saqlandi: {owner_id}")

    except Exception as e:
        logger.error(f"Business media xabarini qayta ishlashda xatolik: {e}", exc_info=True)

@router.deleted_business_messages()
async def business_messages_deleted_handler(event: BusinessMessagesDeleted, bot: Bot):
    """
    Suhbatdosh rasm yoki videoni o'chirib yuborganida bildirishnoma berish!
    """
    try:
        connection_id = event.business_connection_id
        owner_id = await resolve_owner_id(connection_id, bot)
        if not owner_id:
            return

        lang = await get_user_language(owner_id)
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for msg_id in event.message_ids:
            record = await get_media_record(connection_id, event.chat.id, msg_id)
            if record:
                alert_text = get_text(
                    lang,
                    "media_deleted_alert",
                    name=record["sender_name"],
                    username=record["sender_username"],
                    time=now_str
                )
                await bot.send_message(
                    chat_id=owner_id,
                    text=alert_text,
                    parse_mode="HTML"
                )
                logger.info(f"O'chirilgan media haqida bildirishnoma yuborildi: {owner_id}")

    except Exception as e:
        logger.error(f"O'chirilgan business xabarni tekshirishda xatolik: {e}", exc_info=True)
