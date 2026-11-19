import sys
import asyncio
import logging

# Windows konsolida UTF-8 xatoliklarini oldini olish
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from colorama import init, Fore, Style

import config
from database.db import init_db
from handlers.start import router as start_router
from handlers.business import router as business_router
from handlers.direct import router as direct_router

init(autoreset=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(name)s] - %(levelname)s - %(message)s"
)
logger = logging.getLogger("TeleKozBot")

BANNER = f"""
{Fore.CYAN}=============================================================
{Fore.GREEN}        [*]  TELEKO'Z TELEGRAM BOT  [*]
{Fore.YELLOW}  (Faqat rasmlar va videolarni avtomatik saqlovchi bot)
{Fore.CYAN}=============================================================
{Style.RESET_ALL}"""

def check_token() -> str:
    """Bot tokeni borligini tekshirish."""
    token = config.BOT_TOKEN
    if not token or token == "YOUR_BOT_TOKEN_HERE":
        print(f"\n{Fore.RED}[!] BOT_TOKEN topilmadi!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Telegramda @BotFather ga borib /newbot buyrug'i orqali token oling.{Style.RESET_ALL}\n")
        try:
            input_token = input(f"{Fore.CYAN}Bot Tokenini kiriting: {Style.RESET_ALL}").strip()
            if not input_token or ":" not in input_token:
                print(f"{Fore.RED}[X] Noto'g'ri token formati!{Style.RESET_ALL}")
                sys.exit(1)
            
            token = input_token
            env_path = config.BASE_DIR / ".env"
            with open(env_path, "a", encoding="utf-8") as f:
                f.write(f"\nBOT_TOKEN={token}\n")
            print(f"{Fore.GREEN}[+] Token .env fayliga saqlandi!{Style.RESET_ALL}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nBekor qilindi.")
            sys.exit(0)
    return token

async def main():
    print(BANNER)
    token = check_token()

    # Ma'lumotlar bazasini ishga tushirish
    await init_db()
    logger.info("Ma'lumotlar bazasi tayyorlandi.")

    # Bot obyekti
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    dp = Dispatcher()

    # Routerlarni ulash
    dp.include_router(start_router)
    dp.include_router(business_router)
    dp.include_router(direct_router)

    # Bot ma'lumotlarini olish
    me = await bot.get_me()
    print(f"\n{Fore.GREEN}[+] Bot muvaffaqiyatli ishga tushdi!{Style.RESET_ALL}")
    print(f"{Fore.CYAN}Bot nomi:{Style.RESET_ALL} {me.first_name}")
    print(f"{Fore.CYAN}Username:{Style.RESET_ALL} @{me.username}")
    print(f"{Fore.YELLOW}BotFather sozlamasi:{Style.RESET_ALL} @BotFather da /mybots -> Bot Settings -> Business Mode ni ON qiling!")
    print(f"{Fore.WHITE}Dasturni to'xtatish uchun: Ctrl + C{Style.RESET_ALL}\n")

    # Business yangilanishlarni qabul qilish uchun allowed_updates
    allowed_updates = [
        "message",
        "edited_message",
        "callback_query",
        "business_connection",
        "business_message",
        "edited_business_message",
        "deleted_business_messages"
    ]

    # Eski kutilayotgan xabarlarni o'tkazib yuborish
    await bot.delete_webhook(drop_pending_updates=True)

    # Polling boshlash
    await dp.start_polling(bot, allowed_updates=allowed_updates)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print(f"\n{Fore.YELLOW}[!] TeleKo'z Bot to'xtatildi.{Style.RESET_ALL}")
