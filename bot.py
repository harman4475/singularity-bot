import os
import threading
import time
from datetime import datetime, timedelta
import requests
import feedparser
from bs4 import BeautifulSoup
from flask import Flask, request
from deep_translator import GoogleTranslator

# ==================== CONFIGURATION ====================
TELEGRAM_BOT_TOKEN = "7668661293:AAHqp14Jm2bU161k20J31k7faWd"
TELEGRAM_CHANNEL_ID = "-1002447664857"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
SENT_XML_PATH = "sent_html_history.json"
POLL_INTERVAL = 88  # 88 saniye (Hızlı Saniye)
# =======================================================

app = Flask(__name__)

# --- SAĞLIK KONTROLÜ (UPTIMEROBOT İÇİN HAYATİ) ---
@app.route("/health")
def health_check():
    return "OK", 200

@app.route("/")
def home():
    return "Singularity Hub Otonom Akış ve Küresel Radar Sistemidir. Bot aktif çalışıyor!", 200

def get_rss_feed():
    try:
        url = "https://news.google.com/rss?hl=tr&gl=TR&ceid=TR:tr"
        feed = feedparser.parse(url)
        return feed.entries[:5]
    except Exception as e:
        print(f"RSS Çekme Hatası: {e}")
        return []

def translate_text(text):
    try:
        return GoogleTranslator(source='auto', target='en').translate(text)
    except Exception as e:
        print(f"Çeviri Hatası: {e}")
        return text

def rss_poller():
    print("Otonom RSS Poller arka plan iş parçacığı başlatıldı...")
    while True:
        try:
            entries = get_rss_feed()
            for entry in entries:
                title = entry.get('title', '')
                link = entry.get('link', '')
                
                # Çift dilli akış mesajı oluşturma
                translated_title = translate_text(title)
                
                message = (
                    f"🚨 **SİNGULARITY GÜNCEL RADAR** 🚨\n\n"
                    f"🇹🇷 **TR:** {title}\n\n"
                    f"🇬🇧 **EN:** {translated_title}\n\n"
                    f"🔗 [Habere Git]({link})"
                )
                
                payload = {
                    "chat_id": TELEGRAM_CHANNEL_ID,
                    "text": message,
                    "parse_mode": "Markdown",
                    "disable_web_page_preview": False
                }
                
                # Telegram'a gönder
                res = requests.post(TELEGRAM_API_URL, json=payload)
                if res.status_code == 200:
                    print(f"Haber başarıyla gönderildi: {title[:30]}...")
                else:
                    print(f"Telegram Gönderim Hatası: {res.text}")
                
                # Çok sık spam atmasın diye kısa bekleme
                time.sleep(10)
                
        except Exception as e:
            print(f"Poller Döngü Hatası: {e}")
            
        time.sleep(POLL_INTERVAL)

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
                "text": "🤖 Singularity Hub Otonom Modda, Çift Dilli Akış ve Küresel Radar Sistemiyle Aktif!"
            }
            requests.post(url, json=payload)
            
    return "OK", 200

# ==================== BACKGROUND THREAD ====================
try:
    worker = threading.Thread(target=rss_poller, daemon=True)
    worker.start()
    print("✅ Arka plan iş parçacığı ve otonom akış motoru tetiklendi.")
except Exception as e:
    print(f"Thread başlatma hatası: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
