import aiosqlite
from pathlib import Path
from typing import Optional, Dict, Any

DB_PATH = Path(__file__).resolve().parent.parent / "telekoz.db"

async def init_db():
    """Ma'lumotlar bazasini yaratish va jadvallarni sozlash."""
    async with aiosqlite.connect(DB_PATH) as db:
        # Foydalanuvchilar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                username TEXT,
                language TEXT DEFAULT 'uz',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Telegram Business ulanishlari jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS business_connections (
                connection_id TEXT PRIMARY KEY,
                user_id INTEGER,
                is_enabled INTEGER DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Saqlangan rasm va videolar jadvali
        await db.execute("""
            CREATE TABLE IF NOT EXISTS saved_media (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                connection_id TEXT,
                chat_id INTEGER,
                message_id INTEGER,
                sender_name TEXT,
                sender_username TEXT,
                media_type TEXT,
                file_id TEXT,
                caption TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def add_or_update_user(user_id: int, first_name: str, username: Optional[str], language: str = 'uz'):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO users (user_id, first_name, username, language)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                first_name = excluded.first_name,
                username = excluded.username
        """, (user_id, first_name, username, language))
        await db.commit()

async def set_user_language(user_id: int, language: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("UPDATE users SET language = ? WHERE user_id = ?", (language, user_id))
        await db.commit()

async def get_user_language(user_id: int) -> str:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT language FROM users WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 'uz'

async def save_business_connection(connection_id: str, user_id: int, is_enabled: bool):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO business_connections (connection_id, user_id, is_enabled)
            VALUES (?, ?, ?)
            ON CONFLICT(connection_id) DO UPDATE SET
                is_enabled = excluded.is_enabled,
                updated_at = CURRENT_TIMESTAMP
        """, (connection_id, user_id, 1 if is_enabled else 0))
        await db.commit()

async def get_user_by_connection(connection_id: str) -> Optional[int]:
    """Business connection ID bo'yicha bot egasini (user_id) topish."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT user_id FROM business_connections WHERE connection_id = ? AND is_enabled = 1",
            (connection_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_connection_by_user(user_id: int) -> Optional[str]:
    """User ID bo'yicha faol connection_id ni topish."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT connection_id FROM business_connections WHERE user_id = ? AND is_enabled = 1 ORDER BY updated_at DESC LIMIT 1",
            (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def save_media_record(
    user_id: int,
    connection_id: str,
    chat_id: int,
    message_id: int,
    sender_name: str,
    sender_username: str,
    media_type: str,
    file_id: str,
    caption: Optional[str]
):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            INSERT INTO saved_media (
                user_id, connection_id, chat_id, message_id,
                sender_name, sender_username, media_type, file_id, caption
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, connection_id, chat_id, message_id,
            sender_name, sender_username, media_type, file_id, caption
        ))
        await db.commit()

async def get_media_record(connection_id: str, chat_id: int, message_id: int) -> Optional[Dict[str, Any]]:
    """O'chirilgan xabarni qidirish uchun bazadan topish."""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("""
            SELECT * FROM saved_media
            WHERE connection_id = ? AND chat_id = ? AND message_id = ?
            ORDER BY id DESC LIMIT 1
        """, (connection_id, chat_id, message_id)) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None

async def get_user_stats(user_id: int) -> Dict[str, int]:
    """Foydalanuvchining saqlangan rasmlar va videolari statistikasi."""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN media_type = 'photo' THEN 1 ELSE 0 END) as photos,
                SUM(CASE WHEN media_type = 'video' THEN 1 ELSE 0 END) as videos
            FROM saved_media WHERE user_id = ?
        """, (user_id,)) as cursor:
            row = await cursor.fetchone()
            return {
                "total": row[0] or 0,
                "photos": row[1] or 0,
                "videos": row[2] or 0
            }
