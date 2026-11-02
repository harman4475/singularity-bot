import subprocess
import sys

# Eksik kütüphaneleri otomatik yükleme mekanizması
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

# ================= TRANSLATION HELPER =================
def translate_texts(title):
    try:
        # Basit bir tespit ile Türkçe mü yoksa yabancı dil mi anlıyoruz
        # İngilizce ise Türkçeye çevir, Türkçe ise İngilizceye çevir
        translator_tr = GoogleTranslator(source='auto', target='tr')
        translator_en = GoogleTranslator(source='auto', target='en')
        
        # Basitçe hem Türkçe hem İngilizce hallerini oluşturalım
        # Eğer başlık zaten Türkçe ağırlıklıysa ingilizcesini türet, İngilizce ise Türkçesini türet.
        # En garanti yol: Orijinal metni hem tr hem en hedefine çevirmek veya akıllıca harmanlamak.
        
        # Şimdilik en sağlam yöntem: Gelen metni Türkçe ve İngilizce olarak net sunmak.
        translated_tr = translator_tr.translate(title)
        translated_en = translator_en.translate(title)
        
        # Eğer orijinali zaten ingilizce ise translated_tr Türkçedir, translated_en İngilizcedir.
        return translated_tr, translated_en
    except Exception as e:
        print(f"Çeviri hatası: {e}")
        return title, title

# ================= TELEGRAM SENDING (BILINGUAL & RESİMLİ) =================
def send_to_telegram(title, link, image_url):
    if not image_url:
        image_url = "https://images.unsplash.com/photo-1504711434969-e33886168f5c?q=80&w=1000&auto=format&fit=crop"

    # Çift dilli başlık üretimi
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
    print("🌍 Küresel Anlık Çift Dilli Haber Botu Devrede (7/24 Tarama Başladı)...")
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
                        print(f"📢 Yeni Haber İşleniyor: {title}")
                        send_to_telegram(title, link, image_url)
                        
                        history.append(news_id)
                        updated = True
                        time.sleep(2) # Çeviri ve API koruması için bekleme
            except Exception as e:
                print(f"RSS Tarama Hatası ({feed_url}): {e}")

        if updated:
            save_history(history)

        time.sleep(POLL_INTERVAL)

# ================= FLASK KEEP-ALIVE ROUTE =================
@app.route("/")
def home():
    return "Bilingual Global News Intelligence Bot is Running 7/24!"

def run_flask():
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# ================= MAIN ENTRYPOINT =================
if __name__ == "__main__":
    t = threading.Thread(target=rss_poller, daemon=True)
    t.start()
    run_flask()
