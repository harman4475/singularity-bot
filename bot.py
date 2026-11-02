import os
import time
import json
import random
import threading
import feedparser
import requests
from flask import Flask, request
from deep_translator import GoogleTranslator

app = Flask(__name__)

# ================= CONFIGURATION =================
TELEGRAM_BOT_TOKEN = "9068851091:AAFFpGSBNjJa3MlhtzeRiA3iKZ8aJ5ETWxE"
TELEGRAM_CHAT_ID = "-1004449764057"
HISTORY_FILE = "sent_news_history.json"
POLL_INTERVAL = 30  # Döngü hızı (Saniye)

# KÜRESEL VE KARIŞIK AKIŞ İÇİN ULUSLARARASI RSS HAVUZU
LIVE_RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.space.com/home/feed/site.xml",
    "https://techcrunch.com/feed/",
    "https://www.wired.com/feed/rss",
    "https://rss.dw.com/rdf/rss-en-top",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://news.ycombinator.com/rss",
    "https://www.technologyreview.com/feed/"
]

# ================= DÜZENLİ KÜRESEL ANKET & İKİLEM HAVUZU (TR ÜSTTE / EN ALTTA) =================
GLOBAL_POLLS_POOL = [
    {
        "tr": "Yapay Zeka (AGI) önümüzdeki 10 yılda senin mesleğini tamamen ortadan kaldırabilir mi?",
        "en": "Could Artificial Intelligence (AGI) completely eliminate your profession in the next 10 years?",
        "options_tr": ["Evet, kaçış yok", "Hayır, insan şart"],
        "options_en": ["Yes, inevitable", "No, humans needed"]
    },
    {
        "tr": "Mars'a tek yönlü bir koloni yolculuğu teklif edilse, dünyayı arkada bırakıp gider miydin?",
        "en": "If offered a one-way colony trip to Mars, would you leave Earth behind and go?",
        "options_tr": ["Hemen giderim!", "Asla, Dünya güzel"],
        "options_en": ["I'd go right now!", "Never, Earth is home"]
    },
    {
        "tr": "Hafızanı bir buluta yedekleyip ölümsüzleşme şansın olsa, kabul eder miydin?",
        "en": "If you had the chance to back up your memory to a cloud and achieve immortality, would you accept?",
        "options_tr": ["Kesinlikle kabul ederim", "Doğal döngü bozulmamalı"],
        "options_en": ["Definitely accept", "Nature shouldn't be altered"]
    },
    {
        "tr": "Günde sadece 3 saat uyumanı sağlayan ama ömrünü kısaltmayan bir hap olsa içer miydin?",
        "en": "If there was a pill allowing you to sleep only 3 hours a day without shortening your life, would you take it?",
        "options_tr": ["Günde 21 saat bana kalır!", "Risk almam, uykum kutsal"],
        "options_en": ["21 free hours for me!", "No risks, sleep is sacred"]
    },
    {
        "tr": "Tamamen dijital, gerçekçi bir sanal gerçeklik dünyasında ömrünün sonuna kadar yaşamak ister miydin?",
        "en": "Would you want to live out the rest of your life in a completely digital, hyper-realistic virtual reality world?",
        "options_tr": ["Hemen bağlanırım", "Gerçek acı bile tatlıdır"],
        "options_en": ["Plug me in right now", "Real pain over fake bliss"]
    },
    {
        "tr": "Eline ömür boyu çalışmayacağın kadar para geçse ilk ne yapardın?",
        "en": "If you suddenly got enough money to never work again, what would you do first?",
        "options_tr": ["Dünyayı gezerim", "Yeni projeler kurarım"],
        "options_en": ["Travel the world", "Build new projects"]
    },
    {
        "tr": "Yapay zeka kritik bir suç işlediğinde, ceza kod yazana mı yoksa yapay zekanın kendisine mi kesilmeli?",
        "en": "When an AI commits a critical crime, should the punishment go to the developer or the AI itself?",
        "options_tr": ["Kod yazana kesilmeli", "Yapay zekanın kendisine"],
        "options_en": ["To the developer", "To the AI itself"]
    },
    {
        "tr": "İnsanlık için en büyük varoluşsal tehdit hangisidir?",
        "en": "What is the greatest existential threat to humanity?",
        "options_tr": ["Kontrolsüz Yapay Zeka", "İklim Krizi"],
        "options_en": ["Rogue AI", "Climate Crisis"]
    }
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
    if len(history) > 3000:
        history = history[-3000:]
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"History save error: {e}")

def send_to_telegram(title, link, image_url):
    if not image_url:
        image_url = "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1200&auto=format&fit=crop"

    title_tr = title
    title_en = title
    try:
        res_tr = GoogleTranslator(source='auto', target='tr').translate(title)
        if res_tr: title_tr = res_tr
    except: pass

    try:
        res_en = GoogleTranslator(source='auto', target='en').translate(title)
        if res_en: title_en = res_en
    except: pass

    # Çift dilli tek mesaj formatı
    caption = (
        f"🚨 **SINGULARITY HUB // GLOBAL INTEL**\n\n"
        f"🇹🇷 **{title_tr}**\n\n"
        f"🇬🇧 **{title_en}**\n\n"
        f"🔗 [Kaynağa Git / Source Link]({link})"
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

def send_poll_to_telegram():
    poll = random.choice(GLOBAL_POLLS_POOL)
    
    # Soru kısmı alt alta düzenli
    question_text = (
        f"📊 KÜRESEL ANKET / GLOBAL POLL\n\n"
        f"🇹🇷 {poll['tr']}\n\n"
        f"🇬🇧 {poll['en']}\n\n"
        f"👇 Seçeneğini seç ve diğerlerinin oyunu gör!\n"
        f"👇 Vote & see results!"
    )
    
    # Şıklar TR ve EN uyumlu şekilde alt alta/çift dilli
    options = [
        f"{poll['options_tr'][0]} / {poll['options_en'][0]}",
        f"{poll['options_tr'][1]} / {poll['options_en'][1]}"
    ]
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPoll"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "question": question_text[:300],
        "options": options,
        "is_anonymous": False
    }
    
    try:
        requests.post(url, json=payload, timeout=15)
        print("📊 Düzenli ve çift dilli küresel anket kanala gönderildi.")
    except Exception as e:
        print(f"Poll send error: {e}")

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
    print("🚀 Singularity Hub Küresel Karışık Akış Motoru Başlatıldı...")
    
    history = load_history()
    if not history:
        for feed_url in LIVE_RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:
                    nid = getattr(entry, 'id', None) or getattr(entry, 'link', None)
                    if nid: history.append(nid)
            except: pass
        save_history(history)

    counter = 0
    while True:
        try:
            history = load_history()
            updated = False

            counter += 1
            if counter % 3 == 0:
                send_poll_to_telegram()
                time.sleep(10)

            shuffled_feeds = list(LIVE_RSS_FEEDS)
            random.shuffle(shuffled_feeds)

            for feed_url in shuffled_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:5]:
                        news_id = getattr(entry, 'id', None) or getattr(entry, 'link', None)
                        title = getattr(entry, 'title', 'Başlıksız')
                        link = getattr(entry, 'link', '#')

                        if not news_id: continue

                        if news_id not in history:
                            image_url = extract_image(entry)
                            print(f"📢 Yeni Küresel İstihbarat: {title}")
                            send_to_telegram(title, link, image_url)
                            history.append(news_id)
                            updated = True
                            time.sleep(12)
                except Exception as feed_err:
                    print(f"Feed error ({feed_url}): {feed_err}")

            if updated:
                save_history(history)

        except Exception as e:
            print(f"Poller loop error: {e}")

        time.sleep(POLL_INTERVAL)

@app.route("/")
def home():
    return "Singularity Hub Global Mixed Feed is Live!"

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
                "text": "🤖 Singularity Hub Küresel Karışık Akış ve Düzenli Anket Modunda Aktif!"
            }
            requests.post(url, json=payload)
            
    return "OK", 200

# ================= BACKGROUND THREAD =================
try:
    worker = threading.Thread(target=rss_poller, daemon=True)
    worker.start()
    print("✅ Arka plan iş parçacığı başlatıldı.")
except Exception as e:
    print(f"Thread başlatma hatası: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
