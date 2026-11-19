import os
import logging
from telethon import events, TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

import config
from utils.cache import message_cache
from utils.formatters import get_sender_display, format_timestamp, escape_html

logger = logging.getLogger("Anonimus.ViewOnce")

def is_view_once(message) -> tuple[bool, int | None]:
    """Xabar bir martalik yoki taymerli (self-destructing / TTL) media ekanligini tekshiradi."""
    if not message or not message.media:
        return False, None

    media = message.media
    
    # 1. Media obyekti ustidagi ttl_seconds
    ttl = getattr(media, "ttl_seconds", None)
    if ttl:
        return True, ttl

    # 2. Xabar obyekti ustidagi ttl_period
    ttl_period = getattr(message, "ttl_period", None)
    if ttl_period:
        return True, ttl_period

    # 3. Photo yoki Document ichidagi ttl
    if isinstance(media, MessageMediaPhoto) and hasattr(media, "photo"):
        photo_ttl = getattr(media.photo, "ttl_seconds", None)
        if photo_ttl:
            return True, photo_ttl
            
    if isinstance(media, MessageMediaDocument) and hasattr(media, "document"):
        doc_ttl = getattr(media.document, "ttl_seconds", None)
        if doc_ttl:
            return True, doc_ttl

    return False, None

def register_view_once_handlers(client: TelegramClient):
    """
    Bir martalik / taymerli (30s, 10s, 3s, view-once) medialarni ushlash va
    DARHOL @unversal77bot hamda Saqlangan xabarlarga yuborish!
    """

    if not config.SAVE_VIEW_ONCE:
        logger.info("Bir martalik medialarni saqlash funksiyasi o'chirilgan.")
        return

    @client.on(events.NewMessage(func=lambda e: e.is_private and e.chat_id > 0))
    async def view_once_handler(event: events.NewMessage.Event):
        """Taymerli media kelishi bilanoq darhol yuklab olib botga va lichkaga jo'natadi."""
        try:
            message = event.message
            has_ttl, ttl = is_view_once(message)

            if not has_ttl:
                return

            print(f"\n[!] Taymerli media aniqlandi! MsgID: {message.id}, TTL: {ttl}s")

            sender = await event.get_sender()
            sender_name, sender_username, sender_id = get_sender_display(sender, event.sender_id)

            file_prefix = f"view_once_{event.chat_id}_{message.id}"
            target_path = str(config.DOWNLOADS_DIR / file_prefix)

            # O'chib ketmasligi uchun darhol yuklab olamiz
            saved_path = await message.download_media(file=target_path)

            if not saved_path or not os.path.exists(saved_path):
                logger.warning(f"Media yuklab olinmadi: {file_prefix}")
                return

            # Skrinshotdagi kabi chiroyli sarlavha
            time_now = format_timestamp()
            caption = (
                f"🐣 <b>{sender_name}</b>\n"
                f"Taymerli media nusxasi: {time_now.split(' ')[1][:5]}\n"
            )

            if ttl and ttl < 1000:
                caption += f"⏱ Taymer: {ttl} soniya\n"

            if message.text:
                caption += f"\n📝 {escape_html(message.text)}"

            # 1. @unversal77bot chatiga yuborish
            try:
                await client.send_file(
                    "@unversal77bot",
                    saved_path,
                    caption=caption,
                    parse_mode="html"
                )
            except Exception as e:
                logger.error(f"@unversal77bot ga yuborishda xato: {e}")

            # 2. Saqlangan xabarlar (Saved Messages) ga ham yuborish
            try:
                await client.send_file(
                    "me",
                    saved_path,
                    caption=caption,
                    parse_mode="html"
                )
            except Exception as e:
                logger.debug(f"Saved messages ga yuborishda xato: {e}")

            message_cache.increment_view_once()
            print(f"[✓] Taymerli media @unversal77bot va Saqlangan xabarlarga yetkazildi!")

        except Exception as e:
            logger.error(f"Taymerli mediani saqlashda xatolik: {e}", exc_info=True)
