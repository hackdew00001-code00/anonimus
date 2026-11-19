import os
import sys
import asyncio
import logging

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from telethon import TelegramClient
from colorama import init, Fore, Style

import config
from handlers.view_once import register_view_once_handlers
from handlers.anti_delete import register_anti_delete_handlers
from handlers.commands import register_command_handlers
from utils.cache import message_cache

# Rangli konsol
init(autoreset=True)

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
)
# Telethon'ning ortiqcha texnik xabarlarini kamaytirish
logging.getLogger("telethon").setLevel(logging.WARNING)

BANNER = f"""
{Fore.CYAN}=============================================================
{Fore.GREEN}        🎭  ANONIMUS USERBOT  🎭
{Fore.YELLOW}  (Bir martalik media va o'chirilgan xabarlarni saqlovchi)
{Fore.CYAN}=============================================================
{Style.RESET_ALL}"""

async def background_cleanup_task():
    """Har 30 daqiqada keshdagi eski xabarlarni tozalab turadi."""
    while True:
        await asyncio.sleep(1800)
        try:
            message_cache.cleanup_expired()
        except Exception:
            pass

def check_credentials() -> tuple[int, str]:
    """API ma'lumotlarini tekshirish yoki so'rash."""
    api_id = config.API_ID
    api_hash = config.API_HASH

    if not api_id or not api_hash or api_hash == "your_api_hash_here":
        print(f"\n{Fore.RED}[!] Telegram API ma'lumotlari (.env) topilmadi yoki to'liq emas!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Ularni https://my.telegram.org saytidan olishingiz mumkin.{Style.RESET_ALL}\n")
        
        try:
            input_id = input(f"{Fore.CYAN}Telegram API_ID ni kiriting: {Style.RESET_ALL}").strip()
            input_hash = input(f"{Fore.CYAN}Telegram API_HASH ni kiriting: {Style.RESET_ALL}").strip()

            if not input_id.isdigit() or not input_hash:
                print(f"{Fore.RED}[X] Noto'g'ri ma'lumot kiritildi! Dastur to'xtatildi.{Style.RESET_ALL}")
                sys.exit(1)

            api_id = int(input_id)
            api_hash = input_hash

            # .env fayliga saqlab qo'yish
            env_path = config.BASE_DIR / ".env"
            with open(env_path, "w", encoding="utf-8") as f:
                f.write(f"TELEGRAM_API_ID={api_id}\n")
                f.write(f"TELEGRAM_API_HASH={api_hash}\n")
                f.write(f"SAVE_VIEW_ONCE=true\n")
                f.write(f"SAVE_DELETED_MESSAGES=true\n")
            print(f"{Fore.GREEN}[✓] Ma'lumotlar .env fayliga saqlandi!{Style.RESET_ALL}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nBekor qilindi.")
            sys.exit(0)

    return api_id, api_hash

async def main():
    print(BANNER)

    api_id, api_hash = check_credentials()

    print(f"{Fore.YELLOW}[*] Telegram serveriga ulanilmoqda...{Style.RESET_ALL}")
    client = TelegramClient(config.SESSION_NAME, api_id, api_hash)

    # Foydalanuvchi akkauntiga kirish (birinchi marta telefon raqam va kod so'raydi)
    await client.start()

    me = await client.get_me()
    first_name = getattr(me, "first_name", "") or ""
    username = f"@{me.username}" if getattr(me, "username", None) else "Username yo'q"

    print(f"\n{Fore.GREEN}[✓] Muvaffaqiyatli ulandi!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}👤 Hisob egasi:{Style.RESET_ALL} {first_name} ({username})")
    print(f"{Fore.CYAN}🆔 Hisob ID:{Style.RESET_ALL} {me.id}")
    print(f"{Fore.GREEN}[✓] Bir martalik medialarni ushlash:{Style.RESET_ALL} Yoniq")
    print(f"{Fore.GREEN}[✓] O'chirilgan xabarlarni ushlash:{Style.RESET_ALL} Yoniq")
    print(f"\n{Fore.MAGENTA}💡 Eslatma:{Style.RESET_ALL} Barcha ushlangan xabarlar va bir martalik rasmlar")
    print(f"{Fore.MAGENTA}          o'zingizning 'Saqlangan xabarlar'ingizga avtomatik tushadi.{Style.RESET_ALL}\n")
    print(f"{Fore.WHITE}Dasturni to'xtatish uchun: Ctrl + C{Style.RESET_ALL}\n")

    # Handlerlarni ro'yxatdan o'tkazish
    register_view_once_handlers(client)
    register_anti_delete_handlers(client)
    register_command_handlers(client)

    # Orqa fonda keshni tozalab turuvchi vazifa
    asyncio.create_task(background_cleanup_task())

    # Ish jarayonini uzluksiz ushlab turish
    await client.run_until_disconnected()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print(f"\n{Fore.YELLOW}[!] TeleKo'z UserBot to'xtatildi.{Style.RESET_ALL}")
