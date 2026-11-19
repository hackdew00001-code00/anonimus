import html
from datetime import datetime

def escape_html(text: str | None) -> str:
    """Xabardagi maxsus HTML belgilarni xavfsiz holatga keltiradi."""
    if not text:
        return ""
    return html.escape(str(text))

def format_sender_name(sender) -> str:
    """Yuboruvchi ismini formatlash."""
    if not sender:
        return "Noma'lum foydalanuvchi"
    
    first = getattr(sender, "first_name", "") or ""
    last = getattr(sender, "last_name", "") or ""
    full_name = f"{first} {last}".strip()
    return full_name if full_name else "Ismsiz"

def get_sender_display(sender, sender_id: int | None = None) -> tuple[str, str, int | str]:
    """
    Yuboruvchi haqida to'liq ma'lumot qaytaradi:
    (to'liq ism, username yoki havola, id)
    """
    if not sender:
        s_id = sender_id or "Noma'lum"
        return "Noma'lum", "Username yo'q", s_id

    name = format_sender_name(sender)
    username = getattr(sender, "username", None)
    username_str = f"@{username}" if username else "Username yo'q"
    s_id = getattr(sender, "id", sender_id or "Noma'lum")
    
    return escape_html(name), username_str, s_id

def format_timestamp(dt: datetime | None = None) -> str:
    """Sanani chiroyli ko'rinishda qaytarish."""
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")
