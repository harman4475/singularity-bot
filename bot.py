import os
import time
import json
import threading
import feedparser
import requests
from flask import Flask, request
from deep_translator import GoogleTranslator

app = Flask(__name__)

# ================= CONFIGURATION =================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SENIN_BOT_TOKENIN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@SENIN_KANAL_KULANICI_ADIN")
HISTORY_FILE = "sent_news_history.json"
POLL_INTERVAL = 60  # 1 dakika

LIVE_RSS_FEEDS = [
    "https://www.aa.com.tr/tr/rss/default?cat=guncel",
    "https://www.trthaber.com/sondakika.rss",
    "https://www.ntv.com.tr/son-dakika.rss",
    "https://www.haberturk.com/rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.space.com/home/feed/site.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.dw.com/rdf/rss-en-top"
]

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(history):
    if len(history) > 2000:
        history = history[-2000:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"History save error: {e}")

def send_to_telegram(title, link, image_url):
    if not image_url:
        image_url = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000&auto=format&fit=crop"

    try:
        translator_tr = GoogleTranslator(source='auto', target='tr')
        translator_en = GoogleTranslator(source='auto', target='en')
        title_tr = translator_tr.translate(title)
        title_en = translator_en.translate(title)
    except Exception as e:
        print(f"Translation error: {e}")
        title_tr = title
        title_en = title

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
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code != 200:
            payload["parse_mode"] = None
            requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Telegram send error: {e}")

def extract_image(entry):
    if 'media_content' in entry and entry.media_content:
        for m in entry.media_content:
            if 'url' in m: return m['url']
    if 'media_thumbnail' in entry and entry.media_thumbnail:
        for t in entry.media_thumbnail:
            if 'url' in t: return t['url']
    if 'summary' in entry:
        import re
        m = re.search(r'<img[^>]+src="([^">]+)"', entry.summary)
        if m: return m.group(1)
    return None

def rss_poller():
    print("🚀 Otonom RSS Tarama Döngüsü Başlatıldı...")
    
    # Hafızayı kontrol et, yoksa mevcut RSS'yi yükle ki tekrara düşmesin
    history = load_history()
    if not history:
        print("📥 İlk çalıştırma: Eski haberler hafızaya alınıyor...")
        for feed_url in LIVE_RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    nid = getattr(entry, 'id', None) or getattr(entry, 'link', None)
                    if nid: history.append(nid)
            except:
                pass
        save_history(history)

    while True:
        try:
            history = load_history()
            updated = False

            for feed_url in LIVE_RSS_FEEDS:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:3]:
                        news_id = getattr(entry, 'id', None) or getattr(entry, 'link', None)
                        title = getattr(entry, 'title', 'Başlıksız')
                        link = getattr(entry, 'link', '#')

                        if not news_id: continue

                        if news_id not in history:
                            image_url = extract_image(entry)
                            print(f"📢 Yeni Haber Yakalandı: {title}")
                            send_to_telegram(title, link, image_url)
                            history.append(news_id)
                            updated = True
                            time.sleep(3)
                except Exception as feed_err:
                    print(f"Feed error ({feed_url}): {feed_err}")

            if updated:
                save_history(history)

        except Exception as e:
            print(f"Poller loop error: {e}")

        time.sleep(POLL_INTERVAL)

@app.route("/")
def home():
    return "Autonomous Bilingual News Bot is Running Smoothly!"

# Telegram'dan komut aldığında (örn: /post) tepki vermesini sağlayan uç nokta (Webhook)
@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if data and "message" in data:
        msg = data["message"]
        chat_id = msg["chat"]["id"]
        text = msg.get("text", "")
        
        if text.startswith("/post"):
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": "🤖 Bot aktif ve otonom modda çalışıyor usta!"
            }
            requests.post(url, json=payload)
            
    return "OK", 200

# ================= BACKGROUND THREAD =================
try:
    worker = threading.Thread(target=rss_poller, daemon=True)
    worker.start()
    print("✅ Arka plan iş parçacığı başarıyla tetiklendi.")
except Exception as e:
    print(f"Thread başlatma hatası: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
