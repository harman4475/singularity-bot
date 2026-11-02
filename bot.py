import os
import time
import json
import threading
import feedparser
import requests
from flask import Flask

app = Flask(__name__)

# ================= CONFIGURATION =================
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "SENIN_BOT_TOKENIN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "@SENIN_KANAL_KULANICI_ADIN")
HISTORY_FILE = "sent_news_history.json"
POLL_INTERVAL = 120  # Her 2 dakikada bir tarama

# ================= GLOBAL NEWS SOURCE LIST (SADECE HABER AJANSLARI VE MEDYA) =================
LIVE_RSS_FEEDS = [
    # --- TÜRKİYE (Ana Haber Ajansları & Kanallar) ---
    "https://www.aa.com.tr/tr/rss/default?cat=guncel",
    "https://www.trthaber.com/sondakika.rss",
    "https://www.ntv.com.tr/son-dakika.rss",
    "https://www.haberturk.com/rss",
    "https://www.hurriyet.com.tr/rss/anasayfa",
    "https://www.milliyet.com.tr/rss/rssnedir/gundem-rss",

    # --- KUZEY AMERİKA (ABD - Uzay & Resmi Bilim) ---
    "https://www.nasa.gov/news-release/feed/",
    "https://www.space.com/home/feed/site.xml",

    # --- İNGİLTERE & KÜRESEL ---
    "https://feeds.bbci.co.uk/news/world/rss.xml",

    # --- KATAR / ORTA DOĞU ---
    "https://www.aljazeera.com/xml/rss/all.xml",

    # --- ALMANYA / AVRUPA ---
    "https://rss.dw.com/rdf/rss-en-top",
    "https://www.euractiv.com/feed/",

    # --- KUZEY KUTBU / ARKTIK ---
    "https://www.highnorthnews.com/en/rss",

    # --- SİNGAPUR / GÜNEYDOĞU ASYA ---
    "https://www.channelnewsasia.com/api/v1/rss-outlets/cna-rss",

    # --- JAPONYA / UZAK DOĞU ---
    "https://www.asahi.com/rss/asahi/news.rdf",

    # --- HİNDİSTAN / GÜNEY ASYA ---
    "https://economictimes.indiatimes.com/rssfeedsdefault.cms",

    # --- LATİN AMERİKA ---
    "https://en.mercopress.com/rss/",

    # --- AFRİKA KİTASI (Kıta Geneli) ---
    "https://allafrica.com/tools/headlines/rdf/latest/headlines.rdf",

    # --- MISIR / KUZEY AFRİKA ---
    "https://english.ahram.org.eg/NewsAPI/5.xml"
]

# ================= HISTORY MANAGEMENT =================
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

# ================= TELEGRAM SENDING (RESİMLİ) =================
def send_to_telegram(title, link, image_url):
    if not image_url:
        image_url = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000&auto=format&fit=crop"

    caption = f"🚨 **SON DAKİKA / HABER**\n\n🔹 **{title}**\n\n🔗 [Habere Git]({link})"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        if response.status_code != 200:
            payload["parse_mode"] = None
            requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

# ================= EXTRACT IMAGE HELPER =================
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

# ================= BACKGROUND RSS POLL LOOP =================
def rss_poller():
    print("🌍 Küresel Anlık Haber Botu Devrede (7/24 Tarama Başladı)...")
    while True:
        history = load_history()
        updated = False

        for feed_url in LIVE_RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:
                    news_id = getattr(entry, 'id', None) or getattr(entry, 'link', None)
                    title = getattr(entry, 'title', 'Başlıksız Haber')
                    link = getattr(entry, 'link', '#')

                    if not news_id:
                        continue

                    if news_id not in history:
                        image_url = extract_image(entry)
                        print(f"📢 Yeni Haber Paylaşılıyor: {title}")
                        send_to_telegram(title, link, image_url)
                        
                        history.append(news_id)
                        updated = True
                        time.sleep(1.5)
            except Exception as e:
                print(f"RSS Tarama Hatası ({feed_url}): {e}")

        if updated:
            save_history(history)

        time.sleep(POLL_INTERVAL)

# ================= FLASK KEEP-ALIVE ROUTE =================
@app.route("/")
def home():
    return "Global News Intelligence Bot is Running 7/24!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ================= MAIN ENTRYPOINT =================
if __name__ == "__main__":
    t = threading.Thread(target=rss_poller, daemon=True)
    t.start()
    run_flask()
