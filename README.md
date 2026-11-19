# 👁 TeleKo'z Telegram Bot (Faqat Rasm va Videolarni Saqlash)

Ushbu bot aynan siz yuborgan rasmlardagi **@telekoz_bot** kabi ishlaydi. U **Telegram Business (Chatlarni avtomatlashtirish / Чат-боты)** funksiyasi orqali ulanadi va shaxsiy chatlaringizga kelgan **faqat rasmlar va videolarni** (bir martalik, taymerli va oddiy) avtomatik ushlab qolib, botingizga nusxasini saqlab beradi. Agar suhbatdosh o'sha rasm yoki videoni o'chirib yuborsa ham, bot sizga ogohlantirish yuboradi!

---

## 🌟 Imkoniyatlari:
1. **📸 Rasmlarni saqlash:** Shaxsiy chatlarga kelgan bir martalik va har qanday rasmlarni yuboruvchining ismi, ID raqami va vaqti bilan birga saqlaydi.
2. **🎥 Videolarni saqlash:** Har qanday video va dumaloq videolarni (video note) saqlab oladi.
3. **🗑 O'chirilganini aniqlash:** Suhbatdosh rasm yoki videoni o'chirib yuborsa, bot: *"DIQQAT! Suhbatdosh rasm/videoni o'chirdi, lekin u botda saqlanib qoldi!"* deb xabar beradi.
4. **🌐 Ikki tilli interfeys:** O'zbekcha va Ruscha menyu (Skrinshotdagi kabi).
5. **📊 Statistika:** Nechta rasm va video saqlanganini ko'rsatuvchi hisoblagich.

---

## 🚀 O'rnatish va Ishga tushirish (Batafsil)

### 1-qadam: @BotFather orqali bot ochish va sozlash
1. Telegramda rasmiy **[@BotFather](https://t.me/BotFather)** botiga kiring.
2. `/newbot` buyrug'ini yuboring.
3. Botingizga nom (masalan: `Telekoz Media Saver`) va username (masalan: `my_telekoz_bot`) bering.
4. BotFather sizga **API Token** beradi (masalan: `7123456789:AAH...`).
5. ⚠️ **MUHIM QADAM (Business Mode):**
   * BotFather'ga `/mybots` deb yozing va yangi ochgan botingizni tanlang.
   * **Bot Settings** ➔ **Business Mode** bo'limiga kiring.
   * **Turn on** (yoqish) tugmasini bosing! (Shunda botingizni chatlarga ulash imkoni paydo bo'ladi).

---

### 2-qadam: Tokenni kiritish
Loyiha papkasidagi `.env` fayliga tokeningizni yozing yoki dasturni ishga tushirganingizda konsolga kiriting:
```env
BOT_TOKEN=sizning_botfather_tokeningiz
```

---

### 3-qadam: Botni ishga tushirish
Terminalda (PowerShell / CMD):
```powershell
python bot.py
```
Ekranda botingiz muvaffaqiyatli ishga tushgani haqida yashil yozuv chiqadi!

---

### 4-qadam: Botni o'z profilingizga ulash (Skrinshotdagi 3 qadam):
1. Telegram sozlamalariga kiring:
   * **Android / iOS:** Sozlamalar ➔ **Telegram Business** ➔ **Chat-botlar (Chatlarni avtomatlashtirish)**
2. Qidiruv qatoriga o'zingiz ochgan bot username'ini (masalan: `@my_telekoz_bot`) yozing va tanlang.
3. «Javob berishga ruxsat berish»ni yoqing va barcha shaxsiy chatlarni belgilang.
4. **«Qo'shish» (Добавить)** tugmasini bosing.

🎉 **Bo'ldi!** Endi kimdir sizga rasm yoki video yuborsa (hatto bir martalik bo'lsa ham), u darhol ushbu botingizga nusxasi bilan saqlanadi!
