import os
import time
import logging
from telethon import events, TelegramClient

import config
from utils.cache import message_cache, CachedMessage
from utils.formatters import get_sender_display, format_timestamp, escape_html

logger = logging.getLogger("Anonimus.AntiDelete")

def register_anti_delete_handlers(client: TelegramClient):
    """
    O'chirilgan xabarlarni kuzatish hodisalari.
    MUHIM: Faqat shaxsiy chatlar (lichka, chat_id > 0) uchun ishlaydi!
    Guruhlar va kanallar mutlaqo e'tiborga olinmaydi.
    """

    if not config.SAVE_DELETED_MESSAGES:
        logger.info("O'chirilgan xabarlarni saqlash funksiyasi o'chirilgan.")
        return

    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private and e.chat_id > 0))
    async def incoming_private_message_cacher(event: events.NewMessage.Event):
        """Faqat lichkadagi yangi xabarlarni keshga oladi."""
        try:
            # Agar guruh yoki kanal bo'lsa darhol to'xtatish
            if not event.is_private or event.chat_id <= 0:
                return

            message = event.message
            if not message or message.out:
                return

            # Bir martalik medialar alohida view_once tomonidan olinadi
            ttl = getattr(message.media, "ttl_seconds", None) or getattr(message, "ttl_period", None)
            if ttl:
                return

            sender = await event.get_sender()
            sender_name, sender_username, sender_id = get_sender_display(sender, event.sender_id)

            media_path = None
            media_type = None

            if message.media:
                if message.photo:
                    media_type = "photo"
                    file_name = f"cached_{event.chat_id}_{message.id}.jpg"
                    media_path = await message.download_media(file=str(config.CACHE_DIR / file_name))
                elif message.voice:
                    media_type = "voice"
                    file_name = f"cached_{event.chat_id}_{message.id}.ogg"
                    media_path = await message.download_media(file=str(config.CACHE_DIR / file_name))
                elif message.video_note:
                    media_type = "video_note"
                    file_name = f"cached_{event.chat_id}_{message.id}.mp4"
                    media_path = await message.download_media(file=str(config.CACHE_DIR / file_name))

            cached_item = CachedMessage(
                chat_id=event.chat_id,
                msg_id=message.id,
                sender_name=sender_name,
                sender_username=sender_username,
                sender_id=sender_id,
                chat_title="Shaxsiy chat (Lichka)",
                text=message.text or "",
                media_path=media_path if media_path and os.path.exists(media_path) else None,
                media_type=media_type,
                timestamp=time.time(),
                formatted_date=format_timestamp(message.date)
            )

            message_cache.add(cached_item)

        except Exception as e:
            logger.debug(f"Lichka xabarini keshga saqlashda xato: {e}")

    @client.on(events.MessageDeleted)
    async def private_message_deleted_handler(event: events.MessageDeleted.Event):
        """Lichkada suhbatdosh xabarni o'chirib yuborganida ishga tushadi."""
        try:
            # Agar guruh yoki kanal o'chirilishi bo'lsa (chat_id manfiy bo'lsa) - butunlay to'xtatish!
            chat_id = getattr(event, "chat_id", None)
            if chat_id is not None and chat_id < 0:
                return

            for deleted_id in event.deleted_ids:
                cached = message_cache.find_by_msg_id(deleted_id, chat_id)
                # Faqat shaxsiy chatdagi (chat_id > 0) xabar bo'lsa
                if not cached or cached.chat_id <= 0:
                    continue

                print(f"\n[!] Lichkada o'chirilgan xabar ushlandi! Kimdan: {cached.sender_name}")

                alert_text = (
                    f"🗑 <b>Anonimus: Lichkada xabar o'chirildi!</b>\n\n"
                    f"👤 <b>Kimdan:</b> {cached.sender_name} ({cached.sender_username})\n"
                    f"🆔 <b>ID:</b> <code>{cached.sender_id}</code>\n"
                    f"📅 <b>Yozilgan vaqti:</b> {cached.formatted_date}\n"
                    f"⏰ <b>O'chirilgan vaqti:</b> {format_timestamp()}\n"
                )

                if cached.text:
                    alert_text += f"\n📝 <b>O'chirilgan matn:</b>\n<blockquote>{escape_html(cached.text)}</blockquote>"
                else:
                    alert_text += f"\n📝 <b>Media turi:</b> {cached.media_type or 'Fayl'}"

                # 1. Saqlangan xabarlar (Saved Messages) ga yuborish
                if cached.media_path and os.path.exists(cached.media_path):
                    await client.send_file("me", cached.media_path, caption=alert_text, parse_mode="html")
                    try:
                        await client.send_file("@unversal77bot", cached.media_path, caption=alert_text, parse_mode="html")
                    except Exception:
                        pass
                else:
                    await client.send_message("me", alert_text, parse_mode="html")
                    try:
                        await client.send_message("@unversal77bot", alert_text, parse_mode="html")
                    except Exception:
                        pass

                message_cache.increment_deleted()
                print(f"[✓] O'chirilgan xabar Saqlangan xabarlar va @unversal77bot ga muvaffaqiyatli yetkazildi!")

        except Exception as e:
            logger.error(f"Lichkada o'chirilgan xabarni tekshirishda xatolik: {e}", exc_info=True)
