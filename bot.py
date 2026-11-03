import os
import time
import json
import random
import threading
from datetime import datetime
import feedparser
import requests
from flask import Flask, request
from deep_translator import GoogleTranslator

app = Flask(__name__)

# ================= CONFIGURATION =================
TELEGRAM_BOT_TOKEN = "9068851091:AAFFpGSBNjJa3MlhtzeRiA3iKZ8aJ5ETWxE"
TELEGRAM_CHAT_ID = "-1004449764057"
HISTORY_FILE = "sent_news_history.json"
POLL_INTERVAL = 60  # Döngü hızı (Saniye)

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

# ================= GENİŞLETİLMİŞ KÜRESEL ANKET HAVUZU =================
GLOBAL_POLLS_POOL = [
    {
        "tr": "🤖 Yapay Zeka (AGI) önümüzdeki 10 yılda senin mesleğini tamamen ortadan kaldırabilir mi?",
        "en": "🤖 Could Artificial Intelligence (AGI) completely eliminate your profession in the next 10 years?",
        "options": ["Evet, kaçış yok / Yes, inevitable", "Hayır, insan şart / No, humans needed"]
    },
    {
        "tr": "🚀 Mars'a tek yönlü bir koloni yolculuğu teklif edilse, dünyayı arkada bırakıp gider miydin?",
        "en": "🚀 If offered a one-way colony trip to Mars, would you leave Earth behind and go?",
        "options": ["Hemen giderim! / I'd go right now!", "Asla, Dünya güzel / Never, Earth is home"]
    },
    {
        "tr": "🧠 Hafızanı bir buluta yedekleyip ölümsüzleşme şansın olsa, kabul eder miydin?",
        "en": "🧠 If you had the chance to back up your memory to a cloud and achieve immortality, would you accept?",
        "options": ["Kesinlikle kabul ederim / Definitely accept", "Doğal döngü bozulmamalı / Nature shouldn't be altered"]
    },
    {
        "tr": "💊 Günde sadece 3 saat uyumanı sağlayan ama ömrünü kısaltmayan bir hap olsa içer miydin?",
        "en": "💊 If there was a pill allowing you to sleep only 3 hours a day without shortening your life, would you take it?",
        "options": ["Günde 21 saat bana kalır! / 21 free hours for me!", "Risk almam, uykum kutsal / No risks, sleep is sacred"]
    },
    {
        "tr": "🕶️ Tamamen dijital, gerçekçi bir sanal gerçeklik dünyasında ömrünün sonuna kadar yaşamak ister miydin?",
        "en": "🕶️ Would you want to live out the rest of your life in a completely digital, hyper-realistic virtual reality world?",
        "options": ["Hemen bağlanırım / Plug me in right now", "Gerçek acı bile tatlıdır / Real pain over fake bliss"]
    },
    {
        "tr": "💰 Eline ömür boyu çalışmayacağın kadar para geçse ilk ne yapardın?",
        "en": "💰 If you suddenly got enough money to never work again, what would you do first?",
        "options": ["Dünyayı gezerim / Travel the world", "Yeni projeler kurarım / Build new projects"]
    },
    {
        "tr": "⚖️ Yapay zeka kritik bir suç işlediğinde, ceza kod yazana mı yoksa yapay zekanın kendisine mi kesilmeli?",
        "en": "⚖️ When an AI commits a critical crime, should the punishment go to the developer or the AI itself?",
        "options": ["Kod yazana / To the developer", "Yapay zekaya / To the AI"]
    },
    {
        "tr": "🌐 İnsanlık için en büyük varoluşsal tehdit hangisidir?",
        "en": "🌐 What is the greatest existential threat to humanity?",
        "options": ["Kontrolsüz Yapay Zeka / Rogue AI", "İklim Krizi / Climate Crisis"]
    },
    {
        "tr": "🚗 Sürücüsüz otonom araçlara tamamen güvenip arka koltukta uyuyabilir misin?",
        "en": "🚗 Would you completely trust fully autonomous self-driving cars and sleep in the back seat?",
        "options": ["Gözümü kırpmadan uyurum / Sleep soundly", "Asla direksiyonsuz olmaz / Never without a steering wheel"]
    },
    {
        "tr": "🧬 Genetik olarak tasarlanmış (süper zeki veya atletik) bebekler yasal hale gelmeli mi?",
        "en": "🧬 Should genetically engineered (super-smart or athletic) designer babies become legal?",
        "options": ["Evet, evrimsel sıçrama / Yes, evolutionary leap", "Kesinlikle yasaklanmalı / Strictly prohibited"]
    },
    {
        "tr": "🛰️ Dünya dışı akıllı yaşam formu (uzaylılar) keşfedilse, bunu insanlıktan gizlemeliler mi?",
        "en": "🛰️ If an extraterrestrial intelligent life form is discovered, should it be kept secret from humanity?",
        "options": ["Halkla hemen paylaşılmalı / Share immediately", "Panik yaratır, gizlenmeli / Too much panic, hide it"]
    },
    {
        "tr": "⏱️ Zamanda geriye gidip geçmişi değiştirmek mümkün olsa, kelebek etkisinden korkar mıydın?",
        "en": "⏱️ If time travel to the past was possible, would you fear the butterfly effect?",
        "options": ["Geçmişe müdahale edilmez / Don't mess with the past", "Tarihi yeniden yazardım / Rewrite history"]
    }
]

# ================= STRATEJİK & İSTİHBARAT BİLGİ HAVUZU =================
STRATEGIC_INTEL_POOL = [
    {
        "category": "ASKERİ AR-GE & SAVUNMA",
        "tr": "🚀 **Hipersonik Silah Teknolojisi:** Ses hızının 5 katı (Mach 5+) hızla hareket eden bu füzeler, geleneksel hava savunma sistemlerini (Patriot, S-400 vb.) tamamen işlevsiz kılabilir. Çin ve Rusya'nın ardından ABD de bu alanda tungsten kinetik başlıklar üzerinde Ar-Ge çalışmalarını yoğunlaştırmıştır.",
        "en": "🚀 **Hypersonic Weapon Tech:** Moving at Mach 5+, these missiles render traditional air defense systems obsolete."
    },
    {
        "category": "SİBER İSTİHBARAT & DEEP WEB",
        "tr": "🌐 **Soğan Yönlendirme (Onion Routing) Gerçeği:** Deep Web ve Tor ağı, verileri küresel çapta rastgele şifrelenmiş üç farklı düğümden (node) geçirerek IP adresini maskeler. İstihbarat servislerinin bu ağları izlemesi için çıkış düğümlerinde (exit node) derin trafik analizi yapması gerekir.",
        "en": "🌐 **Onion Routing Reality:** Tor masks IP addresses by routing data through three encrypted nodes globally."
    },
    {
        "category": "STRATEJİK SİLAHLAR",
        "tr": "⚛️ **Termonükleer (Hidrojen) Bombalar:** Klasik atom bombalarından (fisyon) farklı olarak füzyon prensibiyle çalışırlar. Başlangıç tetiklemesi için bir atom bombası kullanılarak güneşin merkezindeki sıcaklık ve basınç taklit edilir; yıkıcı güçleri megatonlarca TNT eşdeğerindedir.",
        "en": "⚛️ **Thermonuclear Bombs:** Operating on nuclear fusion, their destructive power reaches megatons of TNT."
    },
    {
        "category": "BUNU BİLİYOR MUYDUNUZ?",
        "tr": "💡 **Kuantum Üstünlüğü (Quantum Supremacy):** Google'ın Sycamore kuantum işlemcisi, dünyanın en güçlü süper bilgisayarının 10.000 yılda çözebileceği bir hesaplama karmaşasını sadece 200 saniyede tamamlamıştır. Bu durum, gelecekteki tüm şifreleme altyapılarını tehdit etmektedir.",
        "en": "💡 **Quantum Supremacy:** Google's processor solved a 10,000-year calculation in just 200 seconds."
    },
    {
        "category": "DİJİTAL MAHREMİYET",
        "tr": "👁️ **Metadata (Üst Veri) Analizi Nedir?:** İstihbarat ajansları için içeriğin kendisinden ziyade *kimin, kime, ne zaman ve nereden* mesaj attığı (metadata) çok daha değerlidir. Büyük veri algoritmaları bu metadata ile bireylerin psikolojik profillerini haritalandırabilir.",
        "en": "👁️ **Metadata Analysis:** For intelligence agencies, *who contacted whom and when* matters more than the message content."
    },
    {
        "category": "STRATEJİK SİLAHLAR",
        "tr": "💣 **Termobarik (Vakum) Bombalar:** Hedef bölgesindeki havadaki oksijeni emerek son derece yüksek sıcaklıkta devasa bir patlama dalgası ve vakum etkisi yaratırlar. Sığınakları, tünelleri ve yeraltı tesislerini etkisiz hale getirmede geleneksel patlayıcılardan çok daha yıkıcıdırlar.",
        "en": "💣 **Thermobaric Bombs:** They consume ambient oxygen to create a high-temperature blast wave and vacuum effect, devastating bunkers."
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

    caption = (
        f"🚨 **SINGULARITY HUB // INTEL**\n\n"
        f"🇹🇷 **{title_tr}**\n\n"
        f"-------------------------------------\n\n"
        f"🇬🇧 **{title_en}**\n\n"
        f"-------------------------------------\n\n"
        f"🔗 [Kaynağa Git / Source Link]({link})"
    )
    
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "👍 Harika / Great", "callback_data": "react_good"},
                {"text": "🔥 Kritik / Critical", "callback_data": "react_fire"},
                {"text": "🚀 Vizyon / Vision", "callback_data": "react_space"}
            ]
        ]
    }

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=15)
        if resp.status_code != 200:
            payload["parse_mode"] = None
            requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Telegram send error: {e}")

def send_strategic_intel_to_telegram():
    intel = random.choice(STRATEGIC_INTEL_POOL)
    
    message_text = (
        f"🛡️ **SINGULARITY HUB // ÖZEL DOSYA & İSTİHBARAT**\n"
        f"📂 *Kategori: {intel['category']}*\n\n"
        f"🇹🇷 {intel['tr']}\n\n"
        f"───────────────────\n\n"
        f"🇬🇧 {intel['en']}"
    )

    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "💡 İlginç / Fascinating", "callback_data": "intel_good"},
                {"text": "🎯 Derin Bilgi / Deep Info", "callback_data": "intel_deep"}
            ]
        ]
    }

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message_text,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup
    }

    try:
        resp = requests.post(url, json=payload, timeout=15)
        print("🛡️ Stratejik istihbarat dosyası kanala gönderildi:", resp.status_code)
    except Exception as e:
        print(f"Strategic Intel send error: {e}")

def send_poll_to_telegram():
    poll = random.choice(GLOBAL_POLLS_POOL)
    
    poll_text = (
        f"📊 KÜRESEL ANKET / GLOBAL POLL\n\n"
        f"🇹🇷 {poll['tr']}\n\n"
        f"───────────────────\n\n"
        f"🇬🇧 {poll['en']}"
    )
    
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPoll"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "question": poll_text[:300],  
        "options": poll["options"],
        "is_anonymous": False
    }
    
    try:
        resp = requests.post(url, json=payload, timeout=15)
        print("📊 Küresel anket başarıyla kanala gönderildi:", resp.status_code)
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
    print("🚀 Singularity Hub Otonom Tarama ve İstihbarat Akışı Başlatıldı...")
    
    history = load_history()
    if not history:
        print("📥 İlk çalıştırma: Eski haberler hafızaya alınıyor...")
        for feed_url in LIVE_RSS_FEEDS:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:2]:
                    nid = getattr(entry, 'id', None) or getattr(entry, 'link', None)
                    if nid: history.append(nid)
            except: pass
        save_history(history)

    last_poll_date_hour = ""
    last_intel_hour = -1

    while True:
        try:
            history = load_history()
            updated = False

            now = datetime.now()
            current_hour = now.hour
            current_date_str = now.strftime("%Y-%m-%d")
            
            # --- ANKET KONTROLÜ: HER 3 SAATTE BİR (00:00, 03:00, 06:00, 09:00, 12:00, 15:00, 18:00, 21:00) ---
            poll_target_hours = [0, 3, 6, 9, 12, 15, 18, 21]
            if current_hour in poll_target_hours:
                time_slot_key = f"{current_date_str}-{current_hour}"
                if last_poll_date_hour != time_slot_key:
                    send_poll_to_telegram()
                    last_poll_date_hour = time_slot_key
                    time.sleep(10)

            # --- STRATEJİK İSTİHBARAT / DOSYA PAYLAŞIMI (Örn. Günde 2 Kez: 09:00 ve 21:00) ---
            intel_target_hours = [9, 21]
            if current_hour in intel_target_hours and last_intel_hour != current_hour:
                send_strategic_intel_to_telegram()
                last_intel_hour = current_hour
                time.sleep(10)

            # --- RSS HABER TARAMA DÖNGÜSÜ ---
            shuffled_feeds = list(LIVE_RSS_FEEDS)
            random.shuffle(shuffled_feeds)

            for feed_url in shuffled_feeds:
                try:
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:2]:
                        news_id = getattr(entry, 'id', None) or getattr(entry, 'link', None)
                        title = getattr(entry, 'title', 'Başlıksız')
                        link = getattr(entry, 'link', '#')

                        if not news_id: continue

                        if news_id not in history:
                            image_url = extract_image(entry)
                            print(f"📢 Yeni İstihbarat Yakalandı: {title}")
                            send_to_telegram(title, link, image_url)
                            history.append(news_id)
                            updated = True
                            time.sleep(15)
                except Exception as feed_err:
                    print(f"Feed error ({feed_url}): {feed_err}")

            if updated:
                save_history(history)

        except Exception as e:
            print(f"Poller loop error: {e}")

        time.sleep(POLL_INTERVAL)

@app.route("/")
def home():
    return "Singularity Hub (Bilingual Intelligence & Deep Tech Feed) is Live!"

@app.route("/health")
def health_check():
    return "OK", 200

@app.route(f"/{TELEGRAM_BOT_TOKEN}", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if data:
        if "callback_query" in data:
            query = data["callback_query"]
            url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
            requests.post(url, json={"callback_query_id": query["id"], "text": "İstihbarat kaydedildi! ⚡"})

        elif "message" in data:
            msg = data["message"]
            chat_id = msg["chat"]["id"]
            text = msg.get("text", "")
            
            if text.startswith("/post"):
                url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
                payload = {
                    "chat_id": chat_id,
                    "text": "🤖 Singularity Hub Otonom İstihbarat Modunda, 3 Saatlik Anket Döngüsü ve Küresel Radar Sistemiyle Aktif!"
                }
                requests.post(url, json=payload)
            
    return "OK", 200

# ================= BACKGROUND THREAD =================
try:
    worker = threading.Thread(target=rss_poller, daemon=True)
    worker.start()
    print("✅ Arka plan iş parçacığı ve istihbarat motoru tetiklendi.")
except Exception as e:
    print(f"Thread başlatma hatası: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
