import logging
import random
import os
import threading
import time
import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
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
    return "Singularity Hub Ultra-Classified Station is active!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ---------------------------------------------------------
# AYARLAR 
# ---------------------------------------------------------
BOT_TOKEN = "9068851091:AAFFpGSBNjJa3MlhtzeRiA3iKZ8aJ5ETWxE"
CHAT_ID = "-1004449764057"

sent_news_ids = set()

LIVE_RSS_FEEDS = [
    "https://www.nasa.gov/news-release/feed/",
    "https://liveuamap.com/rss"
]

ULTRA_CLASSIFIED_HUB = [
    {
        "type": "🛰️ SECRET SATELLITES & OMNISCIENT ORBITS",
        "title_en": "Unknown Military Spy Satellites Tracking Every Move on Earth",
        "title_tr": "Dünya Üzerindeki Her Hareketi İzleyen Gizli Askeri Casus Uydular",
        "desc_en": "Deep background intelligence on black-budget orbital assets.",
        "desc_tr": "Alt-metre zemin çözünürlüğüne sahip gizli bütçeli yörünge varlıkları.",
        "image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1000&auto=format&fit=crop",
        "link": "https://nsarchive.gwu.edu/",
        "tag": "SecretSatellites"
    },
    {
        "type": "🗂️ DEEP WEB ARCHIVES & CLANDESTINE STATE SECRETS",
        "title_en": "Leaked Underground Dossiers: The Truth Governments Hide",
        "title_tr": "Sızdırılan Yeraltı Dosyaları: Hükümetlerin Sakladığı Gerçekler",
        "desc_en": "Unfiltered data dumps from deep web network nodes.",
        "desc_tr": "Gizli hükümet araştırmalarını ifşa eden veri sızıntıları.",
        "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1000&auto=format&fit=crop",
        "link": "https://anonymouse.org",
        "tag": "DeepWebFiles"
    }
]

# Thread-safe doğrudan Telegram HTTP API istekleri (Asenkron çakışmalarını önler)
def send_telegram_message(text, reply_markup=None):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"⚠️ Telegram Mesaj Gönderme Hatası: {e}")
    return None

def send_telegram_photo(photo_url, caption, reply_markup=None):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
        payload = {
            "chat_id": CHAT_ID,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": "HTML"
        }
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
            
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"⚠️ Telegram Fotoğraf Gönderme Hatası: {e}")
    return None

def check_live_news_and_intel():
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
                                f"⚡ <b>SINGULARITY ULTRA-CLASSIFIED INTEL</b>\n"
                                f"🏷️ <code>REAL-TIME FEED ALERT</code>\n\n"
                                f"🚨 <b>{title}</b>\n\n"
                                f"📌 #BreakingNews #SecretSatellites #SingularityHub"
                            )
                            keyboard = {
                                "inline_keyboard": [[{"text": "🔗 Kaynak / Source", "url": link}]]
                            }
                            
                            send_telegram_message(caption, reply_markup=keyboard)
                            print(f"⚡ Gizli akış haberi fırlatıldı: {title}")
                            return True
    except Exception as e:
        print(f"⚠️ Haber tarama hatası: {e}")
    return False

def background_scheduler():
    time.sleep(10)
    counter = 0
    while True:
        try:
            check_live_news_and_intel()
            counter += 1
            if counter >= 5: # Test için süreyi kısalttık, 20 yerine 5 yapabilirsin
                counter = 0
                item = random.choice(ULTRA_CLASSIFIED_HUB)
                caption = (
                    f"🌐 <b>SINGULARITY INTEL: ULTRA-CLASSIFIED ARCHIVES</b>\n"
                    f"🏷️ <code>{item['type']}</code>\n\n"
                    f"🇬🇧 <b>{item['title_en']}</b>\n"
                    f"🇹🇷 <b>{item['title_tr']}</b>\n\n"
                    f"📌 #{item['tag']} #DeepWeb #SingularityHub"
                )
                keyboard = {
                    "inline_keyboard": [[{"text": "🔗 Gizli Dosyayı İncele", "url": item['link']}]]
                }
                send_telegram_photo(item['image'], caption, reply_markup=keyboard)
        except Exception as ex:
            print(f"Döngü hatası: {ex}")
            
        time.sleep(30)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 <b>Ultra-Classified Station Aktif!</b>", parse_mode="HTML")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    
    t_web = threading.Thread(target=run_web)
    t_web.daemon = True
    t_web.start()
    
    t_sched = threading.Thread(target=background_scheduler)
    t_sched.daemon = True
    t_sched.start()
    
    print(f"🚀 Ultra-Classified Station devrede!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
