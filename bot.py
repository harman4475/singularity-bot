import logging
import random
import os
import threading
import time
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram import Bot

# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------------------------------------------------------
# RENDER İÇİN MİNİ WEB SUNUCUSU (Keep-Alive & Health Check)
# ---------------------------------------------------------
web_app = Flask('')

@web_app.route('/')
def home():
    return "Singularity Hub Thread-Safe Bot is active!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ---------------------------------------------------------
# AYARLAR 
# ---------------------------------------------------------
BOT_TOKEN = "9068851091:AAFFpGSBNjJa3MlhtzeRiA3iKZ8aJ5ETWxE"
CHAT_ID = "-1004449764057"
POST_INTERVAL_MINUTES = 30  # Her 30 dakikada bir otomatik atar

# ---------------------------------------------------------
# UZAY, YÖRÜNGE VE GİZLİ SİLAHLAR İSTİHBARAT HAVUZU
# ---------------------------------------------------------
AEROSPACE_SECRET_HUB = [
    {
        "type": "🛰️ ORBITAL MECHANICS & SATELLITE LAUNCH / MÉCANIQUE ORBITALE",
        "title_tr": "Uydular Uzaya Nasıl Fırlatılır ve Hedef Yörüngeye Nasıl Yerleşir?",
        "title_en": "How Satellites Are Launched and Inserted into Target Orbits",
        "title_ru": "Как спутники выводятся на орбиту и занимают заданные позиции",
        "title_ar": "كيف يتم إطلاق الأقمار الصناعية وكيفية وضعها في مداراتها المستهدفة",
        "desc_tr": "Çok aşamalı roketlerin yerçekimi dönüsü (gravity turn) manevraları, kaçış hızları ve Alçak Dünya Yörüngesi (LEO) ile Jeosenkron yörüngelere yerleşme fiziği.",
        "desc_en": "Multi-stage rocket gravity turn maneuvers, escape velocities, and insertion physics into Low Earth Orbit (LEO) and Geostationary orbits.",
        "image": "https://images.unsplash.com/photo-1517976487492-5750f3195933?q=80&w=1000&auto=format&fit=crop",
        "link": "https://www.nasa.gov",
        "tag": "OrbitPhysics"
    },
    {
        "type": "☢️ CLANDESTINE WEAPONS & SECRET R&D / ARMES SECRÈTES",
        "title_tr": "Devletlerin Gizli Silah Projeleri ve Yeni Nesil Stratejik Mühimmat Ar-Ge'si",
        "title_en": "State Secret Weapons Projects and Next-Gen Strategic Ordnance R&D",
        "title_ru": "Секретные оружейные проекты государств и разработка стратегических боеприпасов",
        "title_ar": "مشاريع الأسلحة السرية للدول وتطوير الذخائر الاستراتيجية من الجيل التالي",
        "desc_tr": "Askeri laboratuvarlarda gizlilikle yürütülen hipersonik süzülme araçları, elektromanyetik darbe (EMP) sistemleri ve yeni nesil kompakt başlık teknolojileri.",
        "desc_en": "Classified military laboratory initiatives covering hypersonic glide vehicles, electromagnetic pulse (EMP) systems, and next-gen compact warhead tech.",
        "image": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?q=80&w=1000&auto=format&fit=crop",
        "link": "https://nsarchive.gwu.edu/",
        "tag": "SecretWeapons"
    }
]

# Doğrudan Bot nesnesi üzerinden asenkron bağımsız gönderim fonksiyonu
async def send_scheduled_post():
    bot = Bot(token=BOT_TOKEN)
    item = random.choice(AEROSPACE_SECRET_HUB)
    caption = (
        f"🌐 <b>SINGULARITY INTEL: AEROSPACE & SECRET R&D</b>\n"
        f"🏷️ <code>{item['type']}</code>\n\n"
        f"🇬🇧 <b>{item['title_en']}</b>\n"
        f"🇹🇷 <b>{item['title_tr']}</b>\n"
        f"🇷🇺 <b>{item['title_ru']}</b>\n"
        f"🇸🇦 <b>{item['title_ar']}</b>\n\n"
        f"🇬🇧 <i>{item['desc_en']}</i>\n\n"
        f"🇹🇷 <i>{item['desc_tr']}</i>\n\n"
        f"🔗 <b>YouTube Detaylı Belgesel Analizi Yakında / Video Breakdown Soon</b>\n"
        f"📌 #{item['tag']} #SpaceTech #SecretWeapons #SingularityHub"
    )
    keyboard = [[InlineKeyboardButton("🔗 Teknik Kaynağı İncele / Source", url=item['link'])]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await bot.send_photo(
            chat_id=CHAT_ID,
            photo=item['image'],
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        print("✅ Bağımsız zamanlayıcı ile otomatik post kanala fırlatıldı!")
    except Exception as e:
        print(f"❌ Otomatik gönderim hatası: {e}")

# Arka planda saniyeleri sayan bağımsız döngü iş parçacığı
def background_scheduler():
    # Bot ilk açıldıktan 10 saniye sonra ilk otomatik postu atar
    time.sleep(10)
    import asyncio
    asyncio.run(send_scheduled_post())
    
    # Ardından her X dakikada bir döngüye girer
    while True:
        time.sleep(POST_INTERVAL_MINUTES * 60)
        asyncio.run(send_scheduled_post())

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>Singularity Hub Güvenli Zamanlayıcı Aktif!</b>\n"
        "Otomatik akış bağımsız thread üzerinden kusursuz çalışıyor.", 
        parse_mode="HTML"
    )

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item = random.choice(AEROSPACE_SECRET_HUB)
    caption = (
        f"🌐 <b>SINGULARITY INTEL: AEROSPACE & SECRET R&D</b>\n"
        f"🏷️ <code>{item['type']}</code>\n\n"
        f"🇬🇧 <b>{item['title_en']}</b>\n"
        f"🇹🇷 <b>{item['title_tr']}</b>\n"
        f"🇷🇺 <b>{item['title_ru']}</b>\n"
        f"🇸🇦 <b>{item['title_ar']}</b>\n\n"
        f"🇬🇧 <i>{item['desc_en']}</i>\n\n"
        f"🇹🇷 <i>{item['desc_tr']}</i>\n\n"
        f"🔗 <b>YouTube Detaylı Belgesel Analizi Yakında / Video Breakdown Soon</b>\n"
        f"📌 #{item['tag']} #SpaceTech #SecretWeapons #SingularityHub"
    )
    keyboard = [[InlineKeyboardButton("🔗 Teknik Kaynağı İncele / Source", url=item['link'])]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await context.bot.send_photo(
            chat_id=CHAT_ID,
            photo=item['image'],
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        await update.message.reply_text("🚀 Manuel istihbarat postu fırlatıldı usta!")
    except Exception as e:
        await update.message.reply_text(f"❌ Hata: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("post", post_command))
    
    # Flask sunucusunu arka planda başlatıyoruz
    t_web = threading.Thread(target=run_web)
    t_web.daemon = True
    t_web.start()
    
    # Bağımsız zamanlayıcıyı ayrı bir thread olarak devreye sokuyoruz (Asla takılmaz!)
    t_sched = threading.Thread(target=background_scheduler)
    t_sched.daemon = True
    t_sched.start()
    
    print(f"🚀 Thread-Safe Bot ve Bağımsız Zamanlayıcı Aktif!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
