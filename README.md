# 🎬 KINO BOT

Kino kodlari orqali ishlaydigan to'liq funksional Telegram bot: majburiy
obuna, STANDARD/PREMIUM tariflar, to'liq admin panel. Python + [aiogram 3](https://docs.aiogram.dev/)
asosida yozilgan, Render.com Free Web Service'da ishlashga moslashtirilgan.

## 📁 Loyiha tuzilishi

```
kino_bot/
├── bot.py              # Asosiy ishga tushirish fayli (shu fayl orqali ishga tushadi)
├── config.py            # Environment o'zgaruvchilarini o'qiydi
├── database.py           # SQLite baza va barcha CRUD funksiyalar
├── keyboards.py           # Barcha reply/inline klaviaturalar
├── states.py             # FSM (bosqichli suhbat) holatlari
├── middlewares.py         # Majburiy obuna middleware
├── scheduler.py           # Premium muddatini kuzatuvchi fon vazifasi
├── utils.py              # Yordamchi funksiyalar
├── requirements.txt        # Kerakli kutubxonalar
├── .env.example           # Lokal test uchun namuna
└── handlers/
    ├── user.py            # Foydalanuvchi funksiyalari
    └── admin.py            # Admin panel funksiyalari
```

Hech qanday keraksiz fayl yo'q - har bir fayl aniq bir vazifaga xizmat qiladi.

## ⚙️ Asosiy arxitektura haqida

- **Baza**: SQLite (`database.py`), qo'shimcha kutubxona talab qilmaydi
  (Python bilan birga keladi).
- **Web server**: `aiohttp` yordamida `$PORT`da oddiy `GET /` endpoint
  ochiladi. Bu ham Render'ga "servis tirik" ekanini bildiradi, ham
  UptimeRobot'ning har 5 daqiqalik HEAD so'rovlariga javob beradi (aiohttp
  GET route'lari HEAD so'rovlarni avtomatik qo'llab-quvvatlaydi).

## 🚀 Render.com'da joylashtirish (bosqichma-bosqich)

1. Loyihani GitHub'ga yuklang (yangi repository yarating va shu fayllarni push qiling — `handlers` papkasi ham ichidagi fayllar bilan birga yuklanganiga ishonch hosil qiling).
2. [render.com](https://render.com) → **New +** → **Web Service** → GitHub repo'ni tanlang.
3. Sozlamalar:
   - **Name**: ixtiyoriy (masalan `kino-bot`)
   - **Language/Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: Free
4. **Environment** bo'limiga o'ting va quyidagilarni qo'shing:
   | Key | Value |
   |---|---|
   | `BOT_TOKEN` | @BotFather dan olgan tokeningiz |
   | `ADMIN_ID` | Sizning shaxsiy Telegram ID raqamingiz (masalan @userinfobot orqali oling) |
5. **Create Web Service** tugmasini bosing. Bir necha daqiqadan so'ng bot ishga tushadi.
6. Deploy tugagach, Render sizga `https://kino-bot-xxxx.onrender.com` kabi manzil beradi — shu manzilni keyingi qadamda ishlatasiz.

⚠️ **Muhim**: `DB_PATH` uchun alohida environment o'zgaruvchi qo'shmang -
standart holat (`kino_bot.db`, loyiha papkasida) yetarli. Ammo shuni bilib
qo'ying: Render Free Web Service'da diskning fayllari **redeploy** yoki
**qayta boshlanishda** tozalanishi mumkin, chunki Free reja doimiy diskni
qo'llab-quvvatlamaydi. Agar ma'lumotlaringiz (kinolar, foydalanuvchilar)
doimiy saqlanishi juda muhim bo'lsa, Render Dashboard → **Disks** orqali
pullik doimiy disk ulashingiz mumkin.

Oddiy foydalanish va sinov uchun standart SQLite sozlamasi to'liq yetarli
va hech qanday xatosiz ishlaydi.

## ⏰ UptimeRobot sozlash (botni doim uyg'oq saqlash uchun)

1. [uptimerobot.com](https://uptimerobot.com) ga ro'yxatdan o'ting.
2. **+ Add New Monitor** → **Monitor Type**: `HTTP(s)`.
3. **URL**: Render bergan manzilingiz, masalan `https://kino-bot-xxxx.onrender.com/`
4. **Monitoring Interval**: 5 daqiqa.
5. Saqlang. Shu bilan UptimeRobot har 5 daqiqada shu manzilga so'rov yuborib, bot uxlab qolishining oldini oladi.

## 🤖 Botni birinchi marta ishga tushirish

1. Botga Telegram'da `/start` yozing.
2. Admin panelni ochish uchun `/admin` yozing (faqat `ADMIN_ID` va keyinchalik qo'shilgan adminlar uchun ishlaydi).
3. Avval quyidagilarni sozlashni tavsiya qilamiz:
   - 🎬 **Kino qo'shish** orqali birinchi kinongizni yuklang
   - 📢 **Majburiy kanal qo'shish** orqali obuna talab qilinadigan kanal(lar)ni qo'shing — **bot shu kanal(lar)da admin bo'lishi shart**, aks holda obunani tekshira olmaydi
   - 💵 **Narxlarni belgilash** orqali PREMIUM narxi va muddatini sozlang
   - 💬 **Start xabarini tahrirlash** orqali salomlashuv matnini o'zgartiring

## 🧩 Funksiyalar ro'yxati

**Foydalanuvchi**: majburiy obuna, kino qidirish (kod orqali), STANDARD/PREMIUM
tariflar, hisobim (balans, tarif, muddat), premium tugashiga 24 soat
qolganda avtomatik ogohlantirish, muddat tugagach avtomatik STANDARD ga
tushirish.

**Admin panel** (`/admin`): kino qo'shish/tahrirlash/o'chirish, foydalanuvchi
balansini to'ldirish, premium berish, narxlarni belgilash, majburiy obuna
kanal qo'shish/tahrirlash, statistika (barcha/premium/standard
foydalanuvchilar, kanallar, TOP-15 to'ldiruvchi, adminlar), admin
qo'shish/tahrirlash (ASOSIY / SUB-ADMIN / ODDIY darajalar), ommaviy xabar
yuborish, reklama (matn/rasm/audio + tugma), matn/username tahrirlash,
start xabarini tahrirlash.

## ✅ Kod sifatida qanday tekshirilgan

Ushbu loyihadagi barcha `.py` fayllar sintaksis bo'yicha tekshirilgan
(`py_compile`), va butun ma'lumotlar bazasi qatlami, barcha foydalanuvchi
va admin funksiyalari soxtalashtirilgan (mock) aiogram muhitida to'liq
ishga tushirilib, haqiqiy senariylar (kino qo'shish, tahrirlash, o'chirish,
balans to'ldirish, premium berish, kanal boshqarish, admin boshqarish,
ommaviy xabar, reklama, majburiy obuna middleware'i va h.k.) muvaffaqiyatli
sinovdan o'tkazilgan. Bu esa import xatolari, noto'g'ri o'zgaruvchi nomlari
va mantiqiy xatolarning oldini oladi.

Faqat haqiqiy Telegram serverlariga ulanish real muhitda birinchi marta
ishga tushirilganda tekshiriladi — shuning uchun `requirements.txt`da
versiyalar oraliq (`>=`, `<`) ko'rinishida belgilangan, bu esa Render'da
"kutubxona topilmadi" xatosining oldini oladi.

## 🛠 Muammolarni bartaraf etish

- **"BOT_TOKEN topilmadi" xatosi** → Render → Environment bo'limida `BOT_TOKEN` to'g'ri kiritilganini tekshiring.
- **Bot obunani tekshira olmayapti** → bot qo'shgan kanalingizda **admin** ekanligiga ishonch hosil qiling.
- **Bot uxlab qolyapti** → UptimeRobot monitoringi to'g'ri manzilga sozlanganini va interval 5 daqiqa qilib qo'yilganini tekshiring.
- **Ma'lumotlar redeploy'dan keyin yo'qoladi** → yuqoridagi "Render.com'da joylashtirish" bo'limidagi Disk haqidagi izohni o'qing.
- **`ModuleNotFoundError: No module named 'handlers'`** → GitHub repo'ingizda `handlers` papkasi (ichida `user.py`, `admin.py`, `__init__.py` bilan birga) mavjudligini tekshiring.
