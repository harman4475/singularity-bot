import logging
import random
import os
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET
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
    return "Singularity Hub Ultimate OSINT Bot is active!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ---------------------------------------------------------
# AYARLAR 
# ---------------------------------------------------------
BOT_TOKEN = "9068851091:AAFFpGSBNjJa3MlhtzeRiA3iKZ8aJ5ETWxE"
CHAT_ID = "-1004449764057"

sent_news_ids = set()

# Yerleşik kütüphaneyle taranacak RSS kaynakları
LIVE_RSS_FEEDS = [
    "https://www.nasa.gov/news-release/feed/",
    "https://liveuamap.com/rss"
]

AEROSPACE_SECRET_HUB = [
    {
        "type": "🛰️ ORBITAL MECHANICS & SATELLITE LAUNCH",
        "title_tr": "Uydular Uzaya Nasıl Fırlatılır ve Hedef Yörüngeye Nasıl Yerleşir?",
        "title_en": "How Satellites Are Launched and Inserted into Target Orbits",
        "desc_tr": "Çok aşamalı roketlerin yerçekimi dönüsü manevraları ve Alçak Dünya Yörüngesi (LEO) fiziksel hesaplamaları.",
        "desc_en": "Multi-stage rocket gravity turn maneuvers and Low Earth Orbit insertion physics.",
        "image": "https://images.unsplash.com/photo-1517976487492-5750f3195933?q=80&w=1000&auto=format&fit=crop",
        "link": "https://www.nasa.gov",
        "tag": "OrbitPhysics"
    },
    {
        "type": "☢️ CLANDESTINE WEAPONS & SECRET R&D",
        "title_tr": "Devletlerin Gizli Silah Projeleri ve Yeni Nesil Stratejik Mühimmat Ar-Ge'si",
        "title_en": "State Secret Weapons Projects and Next-Gen Strategic Ordnance R&D",
        "desc_tr": "Askeri laboratuvarlarda yürütülen hipersonik süzülme araçları ve elektromanyetik darbe sistemleri.",
        "desc_en": "Classified military laboratory initiatives covering hypersonic glide vehicles and EMP systems.",
        "image": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?q=80&w=1000&auto=format&fit=crop",
        "link": "https://nsarchive.gwu.edu/",
        "tag": "SecretWeapons"
    }
]

POLL_POOL = [
    {
        "question": "🌐 Sizce gizli askerî projeler ve yeni nesil silahlar kamuoyundan ne kadar saklanabiliyor?",
        "options": ["Tamamen gizleniyor", "Zaten sızdırılıyor", "Bilinmiyor"]
    },
    {
        "question": "🚀 Yakın gelecekte uzay hâkimiyeti küresel savaşların kaderini belirler mi?",
        "options": ["Kesinlikle belirler", "Kısmen etkiler", "Etkilemez"]
    }
]

def check_live_news_and_intel(bot):
    try:
        for feed_url in LIVE_RSS_FEEDS:
            req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                channel = root.find('channel')
                if channel is not None:
                    item = channel.find('item')
                    if item is not None:
                        title_el = item.find('title')
                        link_el = item.find('link')
                        guid_el = item.find('guid')
                        
                        title = title_el.text if title_el is not None else "Son Dakika İstihbarat"
                        link = link_el.text if link_el is not None else "https://t.me"
                        news_id = guid_el.text if guid_el is not None else title
                        
                        if news_id not in sent_news_ids:
                            sent_news_ids.add(news_id)
                            if len(sent_news_ids) > 100:
                                sent_news_ids.pop()
                                
                            caption = (
                                f"⚡ <b>SINGULARITY LIVE BREAKING INTEL</b>\n"
                                f"🏷️ <code>REAL-TIME FEED ALERT</code>\n\n"
                                f"🚨 <b>{title}</b>\n\n"
                                f"🇹🇷 <i>[Anlık Ajans Verisi Yakalandı]</i>\n"
                                f"🔗 <b>YouTube Stratejik Analiz Yakında</b>\n"
                                f"📌 #BreakingNews #OSINT #SingularityHub"
                            )
                            keyboard = [[InlineKeyboardButton("🔗 Canlı Kaynak", url=link)]]
                            
                            import asyncio
                            asyncio.run(bot.send_message(
                                chat_id=CHAT_ID,
                                text=caption,
                                parse_mode="HTML",
                                reply_markup=InlineKeyboardMarkup(keyboard)
                            ))
                            print(f"⚡ Anlık haber fırlatıldı: {title}")
                            return True
    except Exception as e:
        print(f"⚠️ Haber tarama hatası: {e}")
    return False

def background_scheduler():
    bot = Bot(token=BOT_TOKEN)
    time.sleep(10)
    counter = 0
    while True:
        try:
            has_news = check_live_news_and_intel(bot)
            counter += 1
            if counter >= 20:
                counter = 0
                choice_type = random.choice(["post", "poll"])
                if choice_type == "post":
                    item = random.choice(AEROSPACE_SECRET_HUB)
                    caption = (
                        f"🌐 <b>SINGULARITY INTEL: AEROSPACE & SECRET R&D</b>\n"
                        f"🏷️ <code>{item['type']}</code>\n\n"
                        f"🇬🇧 <b>{item['title_en']}</b>\n"
                        f"🇹🇷 <b>{item['title_tr']}</b>\n\n"
                        f"🇬🇧 <i>{item['desc_en']}</i>\n"
                        f"🇹🇷 <i>{item['desc_tr']}</i>\n\n"
                        f"📌 #{item['tag']} #SingularityHub"
                    )
                    keyboard = [[InlineKeyboardButton("🔗 Kaynak", url=item['link'])]]
                    import asyncio
                    asyncio.run(bot.send_photo(chat_id=CHAT_ID, photo=item['image'], caption=caption, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(keyboard)))
                else:
                    poll = random.choice(POLL_POOL)
                    import asyncio
                    asyncio.run(bot.send_poll(chat_id=CHAT_ID, question=poll["question"], options=poll["options"], is_anonymous=False))
        except Exception as ex:
            print(f"Döngü hatası: {ex}")
            
        time.sleep(30)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 <b>Ultimate OSINT Bot Aktif!</b> Hata giderildi, sistem stabil.", parse_mode="HTML")

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    item = random.choice(AEROSPACE_SECRET_HUB)
    caption = f"🌐 <b>MANUAL INTEL DROP</b>\n🏷️ <code>{item['type']}</code>\n\n🇹🇷 <b>{item['title_tr']}</b>"
    await bot.send_photo(chat_id=CHAT_ID, photo=item['image'], caption=caption, parse_mode="HTML")
    await update.message.reply_text("🚀 Manuel test postu atıldı usta!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("post", post_command))
    
    t_web = threading.Thread(target=run_web)
    t_web.daemon = True
    t_web.start()
    
    t_sched = threading.Thread(target=background_scheduler)
    t_sched.daemon = True
    t_sched.start()
    
    print(f"🚀 Hatasız Ultimate OSINT Bot devrede!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
