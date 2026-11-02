import subprocess
import sys

def auto_install():
    required_packages = ["flask", "feedparser", "requests", "gunicorn", "deep-translator"]
    for package in required_packages:
        try:
            if package == "deep-translator":
                __import__("deep_translator")
            else:
                __import__(package)
        except ImportError:
            print(f"'{package}' kütüphanesi yükleniyor...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

auto_install()

import os
import time
import json
import threading
import feedparser
import requests
from flask import Flask
from deep_translator import GoogleTranslator

app = Flask(__name__)

# ================= CONFIGURATION =================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SENIN_BOT_TOKENIN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@SENIN_KANAL_KULANICI_ADIN")
HISTORY_FILE = "sent_news_history.json"
POLL_INTERVAL = 60  # 1 dakikaya indirildi

LIVE_RSS_FEEDS = [
    "https://www.aa.com.tr/tr/rss/default?cat=guncel",
    "https://www.trthaber.com/sondakika.rss",
    "https://www.ntv.com.tr/son-dakika.rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.space.com/home/feed/site.xml",
    "https://www.aljazeera.com/xml/rss/all.xml"
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    if len(history) > 1000:
        history = history[-1000:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Geçmiş kaydedilirken hata: {e}")

def translate_texts(title):
    try:
        translator_tr = GoogleTranslator(source='auto', target='tr')
        translator_en = GoogleTranslator(source='auto', target='en')
        
        translated_tr = translator_tr.translate(title)
        translated_en = translator_en.translate(title)
        return translated_tr, translated_en
    except Exception as e:
        print(f"Çeviri hatası: {e}")
        return title, title

def send_to_telegram(title, link, image_url):
    if not image_url:
        image_url = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000&auto=format&fit=crop"

    title_tr, title_en = translate_texts(title)

    caption = (
        f"🚨 **SON DAKİKA / BREAKING NEWS**\n\n"
        f"🇹🇷 **{title_tr}**\n\n"
        f"🇬🇧 **{title_en}**\n\n"
        f"🔗 [Habere Git / Read More]({link})"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        print(f"Telegram Yanıt Kodu: {response.status_code}")
        if response.status_code != 200:
            print(f"Telegram Hata Detayı: {response.text}")
            payload["parse_mode"] = None
            requests.post(url, json=payload, timeout=15)
        else:
            print(f"✅ Başarıyla Gönderildi: {title_tr}")
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def extract_image(entry):
    if 'media_content' in entry and entry.media_content:
        for media in entry.media_content:
            if 'url' in media:
                return media['url']
                
    if 'media_thumbnail' in entry and entry.media_thumbnail:
        for thumb in entry.media_thumbnail:
            if 'url' in thumb:
                return thumb['url']
                
    if 'summary' in entry:
        import re
        img_match = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
        if img_match:
            return img_match.group(1)
            
    return None

def rss_poller():
    print("🌍 Küresel Anlık Çift Dilli Haber Botu Devrede (7/24 Tarama Başladı)...")
    while True:
        try:
            history = load_history()
            updated = False

            for feed_url in LIVE_RSS_FEEDS:
                print(f"Taranıyor: {feed_url}")
                try:
                    feed = feedparser.parse(feed_url)
                    print(f"Kaynakta {len(feed.entries)} haber bulundu.")
                    for entry in feed.entries[:3]:
                        news_id = getattr(entry, 'id', None) or getattr(entry, 'link', None)
                        title = getattr(entry, 'title', 'Başlıksız Haber')
                        link = getattr(entry, 'link', '#')

                        if not news_id:
                            continue

                        if news_id not in history:
                            image_url = extract_image(entry)
                            print(f"📢 Yeni Haber İşleniyor: {title}")
                            send_to_telegram(title, link, image_url)
                            
                            history.append(news_id)
                            updated = True
                            time.sleep(3) 
                except Exception as feed_err:
                    print(f"RSS Kaynak Hatası ({feed_url}): {feed_err}")

            if updated:
                save_history(history)

        except Exception as loop_err:
            print(f"Döngü genel hatası: {loop_err}")

        print(f"Tarama turu tamamlandı. {POLL_INTERVAL} saniye bekleniyor...")
        time.sleep(POLL_INTERVAL)

@app.route("/")
def home():
    return "Bilingual Global News Intelligence Bot is Running 7/24!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    t = threading.Thread(target=rss_poller, daemon=True)
    t.start()
    run_flask()
