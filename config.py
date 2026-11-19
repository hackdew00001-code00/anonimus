import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

# .env yuklash
load_dotenv(BASE_DIR / ".env")

# Telegram Bot Token (@BotFather dan olinadi)
BOT_TOKEN = os.getenv("BOT_TOKEN", "")

# Admin ID lari (vergul bilan ajratilgan: 123456,789012)
ADMIN_IDS = [
    int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",")
    if x.strip().isdigit()
]

# Telethon UserBot parametrlari (agar kerak bo'lsa)
API_ID_RAW = os.getenv("TELEGRAM_API_ID", "")
API_ID = int(API_ID_RAW) if API_ID_RAW.isdigit() else None
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSION_NAME = str(BASE_DIR / "telekoz_session")

# Papkalar
DOWNLOADS_DIR = BASE_DIR / "downloads"
CACHE_DIR = BASE_DIR / "cache"

# Sozlamalar
SAVE_VIEW_ONCE = os.getenv("SAVE_VIEW_ONCE", "true").lower() == "true"
SAVE_DELETED_MESSAGES = os.getenv("SAVE_DELETED_MESSAGES", "true").lower() == "true"
DOWNLOADS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
