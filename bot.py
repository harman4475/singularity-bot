import logging
import random
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

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
    return "Singularity Hub Aerospace & Secret Weapons Bot is active!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ---------------------------------------------------------
# AYARLAR 
# ---------------------------------------------------------
BOT_TOKEN = "9068851091:AAFFpGSBNjJa3MlhtzeRiA3iKZ8aJ5ETWxE"
CHAT_ID = "-1004449764057"
POST_INTERVAL_MINUTES = 30  # Akış sıklığı

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
    },
    {
        "type": "🚀 ADVANCED PROPULSION & DEFENSE / PROPULSION AVANCÉE",
        "title_tr": "Yapay Zeka Destekli Güdümlü Sistemler ve Uzay Tabanlı Gözetleme Uyduları",
        "title_en": "AI-Powered Guidance Systems and Space-Based Surveillance Satellites",
        "title_ru": "Системы наведения на базе ИИ и космические спутники наблюдения",
        "title_ar": "أنظمة التوجيه المدعومة بالذكاء الاصطناعي وأقمار المراقبة الفضائية",
        "desc_tr": "Yörüngede görev yapan askeri keşif uydularının optik çözünürlük sınırları ve yapay zeka tabanlı otonom yörünge düzeltme motorları.",
        "desc_en": "Optical resolution limits of orbiting military reconnaissance satellites and AI-driven autonomous orbital adjustment thrusters.",
        "image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1000&auto=format&fit=crop",
        "link": "https://www.space.com",
        "tag": "SpaceDefense"
    }
]

async def send_aerospace_post(context: ContextTypes.DEFAULT_TYPE):
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
        print("✅ Uzay ve gizli silahlar istihbarat postu fırlatıldı!")
    except Exception as e:
        print(f"❌ Gönderim hatası: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>Singularity Hub Aerospace & R&D Üssü Aktif!</b>\n"
        "Yörünge mekanikleri, uydu teknolojileri ve gizli silah arşivleri yayında.", 
        parse_mode="HTML"
    )

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_aerospace_post(context)
    await update.message.reply_text("🚀 Uzay ve gizli silah raporu kanala fırlatıldı usta!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("post", post_command))
    
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(lambda ctx: send_aerospace_post(ctx), interval=POST_INTERVAL_MINUTES * 60, first=10)
    
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
    
    print(f"🚀 Aerospace & Secret Weapons Bot aktif!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
