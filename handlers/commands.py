import time
from telethon import events, TelegramClient

from utils.cache import message_cache

def register_command_handlers(client: TelegramClient):
    """Faqat hisob egasining o'zi ishlatishi mumkin bo'lgan buyruqlar."""

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.ping$"))
    async def ping_handler(event: events.NewMessage.Event):
        start = time.time()
        reply_msg = await event.edit("🏓 Hisoblanmoqda...")
        delta = (time.time() - start) * 1000
        await reply_msg.edit(
            f"🏓 <b>Pong!</b>\n"
            f"⚡️ Tezlik: <code>{delta:.1f} ms</code>\n"
            f"🎭 <b>Anonimus UserBot faol ishlamoqda!</b>",
            parse_mode="html"
        )

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.(anonim|anonimus|stats|telekoz)$"))
    async def stats_handler(event: events.NewMessage.Event):
        uptime_seconds = int(time.time() - message_cache.start_time)
        hours, remainder = divmod(uptime_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{hours} soat, {minutes} daqiqa, {seconds} soniya"

        stats_text = (
            f"🎭 <b>Anonimus UserBot Statistikasi:</b>\n\n"
            f"🟢 <b>Holati:</b> Faol\n"
            f"⏳ <b>Ish vaqti:</b> {uptime_str}\n"
            f"📥 <b>Ushlab qolingan bir martalik medialar:</b> <code>{message_cache.view_once_count}</code> ta\n"
            f"🗑 <b>Ushlab qolingan o'chirilgan xabarlar:</b> <code>{message_cache.deleted_caught_count}</code> ta\n"
            f"📦 <b>Keshdagi xabarlar soni:</b> <code>{len(message_cache._cache)}</code> ta\n\n"
            f"<i>Barcha saqlangan ma'lumotlar 'Saqlangan xabarlar' (Saved Messages) da mavjud.</i>"
        )
        await event.edit(stats_text, parse_mode="html")

    @client.on(events.NewMessage(outgoing=True, pattern=r"^\.help$"))
    async def help_handler(event: events.NewMessage.Event):
        help_text = (
            f"🎭 <b>Anonimus UserBot Buyruqlari:</b>\n\n"
            f"🔹 <code>.ping</code> — Bot tezligi va ish faoliyatini tekshirish\n"
            f"🔹 <code>.stats</code> yoki <code>.anonim</code> — Saqlangan media va xabarlar statistikasi\n"
            f"🔹 <code>.help</code> — Ushbu yordam oynasi\n\n"
            f"<i>Eslatma: Bu buyruqlarni faqat o'zingiz yuborganingizda ishlaydi.</i>"
        )
        await event.edit(help_text, parse_mode="html")
