import os
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Optional

@dataclass
class CachedMessage:
    chat_id: int
    msg_id: int
    sender_name: str
    sender_username: str
    sender_id: int | str
    chat_title: str
    text: str
    media_path: Optional[str]
    media_type: Optional[str]
    timestamp: float
    formatted_date: str

class MessageCache:
    """
    O'chirilgan xabarlarni aniqlash uchun yaqinda kelgan xabarlarni saqlovchi kesh.
    Avtomatik ravishda eski xabarlar va fayllarni tozalab turadi.
    """
    def __init__(self, max_items: int = 5000, ttl_hours: int = 48):
        self.max_items = max_items
        self.ttl_seconds = ttl_hours * 3600
        # Kalit: (chat_id, msg_id)
        self._cache: OrderedDict[tuple[int, int], CachedMessage] = OrderedDict()
        
        # Statistika
        self.view_once_count: int = 0
        self.deleted_caught_count: int = 0
        self.start_time: float = time.time()

    def add(self, message: CachedMessage):
        key = (message.chat_id, message.msg_id)
        # Agar mavjud bo'lsa yangilaymiz
        if key in self._cache:
            self._cache.move_to_end(key)
        self._cache[key] = message

        # Hajm chegarasidan oshsa eng eskisini tozalaymiz
        if len(self._cache) > self.max_items:
            oldest_key, oldest_msg = self._cache.popitem(last=False)
            self._cleanup_media(oldest_msg.media_path)

    def get(self, chat_id: int, msg_id: int) -> Optional[CachedMessage]:
        key = (chat_id, msg_id)
        return self._cache.get(key)

    def find_by_msg_id(self, msg_id: int, chat_id: Optional[int] = None) -> Optional[CachedMessage]:
        """Xabar id bo'yicha qidirish (agar chat_id aniq bo'lmasa)."""
        if chat_id is not None:
            return self.get(chat_id, msg_id)
        
        # chat_id berilmagan bo'lsa, oxirgi keshdan qidirish
        for (c_id, m_id), msg in reversed(self._cache.items()):
            if m_id == msg_id:
                return msg
        return None

    def increment_view_once(self):
        self.view_once_count += 1

    def increment_deleted(self):
        self.deleted_caught_count += 1

    def _cleanup_media(self, media_path: Optional[str]):
        """Keshdan chiqarilgan eski media faylni diskdan o'chirish."""
        if media_path and os.path.exists(media_path):
            try:
                os.remove(media_path)
            except Exception:
                pass

    def cleanup_expired(self):
        """Muddati o'tgan xabarlarni tozalash."""
        now = time.time()
        expired_keys = [
            k for k, msg in self._cache.items()
            if now - msg.timestamp > self.ttl_seconds
        ]
        for k in expired_keys:
            msg = self._cache.pop(k)
            self._cleanup_media(msg.media_path)

# Global kesh obyekti
message_cache = MessageCache()
