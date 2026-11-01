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
from telegram import Update
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
sent_archive_tags = []

# 🌐 DÜNYANIN DÖRT BİR YANINDAN ENTASTE VE CANLI HABER AKIŞLARI
LIVE_RSS_FEEDS = [
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.dw.com/rdf/rss-en-top",
    "https://www.space.com/home/feed/site.xml",
    "https://www.technologyreview.com/feed/",
    "https://www.nasa.gov/news-release/feed/"
]

# 🕵️ GİZLİ SATELLITE, DEEP WEB VE SANSÜRSÜZ İSTİHBARAT HAVUZU
ULTRA_CLASSIFIED_HUB = [
    {
        "type": "🛰️ SECRET SATELLITES & OMNISCIENT ORBITS",
        "title_en": "Unknown Military Spy Satellites Tracking Every Move on Earth",
        "title_tr": "Dünya Üzerindeki Her Hareketi İzleyen Gizli Askeri Casus Uydular",
        "desc_en": "Deep background intelligence on black-budget orbital assets capable of sub-meter resolution.",
        "desc_tr": "Alt-metre çözünürlüğe sahip gizli bütçeli yörünge varlıkları hakkında derin arka plan.",
        "image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1000&auto=format&fit=crop",
        "link": "https://nsarchive.gwu.edu/",
        "tag": "SecretSatellites"
    },
    {
        "type": "🗂️ DEEP WEB ARCHIVES & CLANDESTINE STATE SECRETS",
        "title_en": "Leaked Underground Dossiers: The Truth Governments Hide from Public",
        "title_tr": "Sızdırılan Yeraltı Dosyaları: Hükümetlerin Halktan Sakladığı Gerçekler",
        "desc_en": "Unfiltered data dumps from deep web network nodes revealing covert research.",
        "desc_tr": "Gizli hükümet araştırmalarını ve unutulmuş anlaşmaları ifşa eden sızıntılar.",
        "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1000&auto=format&fit=crop",
        "link": "https://anonymouse.org",
        "tag": "DeepWebFiles"
    },
    {
        "type": "☢️ UNKNOWN WEAPONS R&D & BLACK PROJECTS",
        "title_en": "Classified Electromagnetic Energy Weapons and Underground R&D Labs",
        "title_tr": "Sınıflandırılmış Elektromanyetik Enerji Silahları ve Gizli Laboratuvarlar",
        "desc_en": "Deep investigative breakdowns of kinetic impactors and directed-energy prototypes.",
        "desc_tr": "Kinetik çarpıştırıcılar ve yönlendirilmiş enerji prototipleri hakkında incelemeler.",
        "image": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?q=80&w=1000&auto=format&fit=crop",
        "link": "https://www.nsa.gov",
        "tag": "BlackProjects"
    },
    {
        "type": "🧬 QUANTUM ANOMALIES & SECRET LABS",
        "title_en": "Subterranean Quantum Computing Facilities and Reality Distortion Tests",
        "title_tr": "Yeraltı Kuantum Bilgisayar Tesisleri ve Gerçeklik Bükme Testleri",
        "desc_en": "Leaked documents regarding deep underground particle collisions and alternate frequency experiments.",
        "desc_tr": "Derin yeraltı parçacık çarpışmaları ve alternatif frekans deneyleri hakkındaki sızdırılmış belgeler.",
        "image": "https://images.unsplash.com/photo-1507413245164-6160d8298b31?q=80&w=1000&auto=format&fit=crop",
        "link": "https://home.cern/",
        "tag": "QuantumLeaks"
    }
]

# 📊 KANAL İÇİN ETKİLEŞİMLİ ANKET HAVUZU
POLL_POOL = [
    {
        "question": "🌐 Sizce uzaydaki gizli askeri casus uydular ve black-project projeleri halktan daha ne kadar saklanabilir?",
        "options": ["Çoktan ifşa oldu / Already exposed", "Hâlâ tamamen gizli / Fully secret", "Bilinmiyor / Unknown"]
    },
    {
        "question": "🕵️ Deep web sızıntıları ve devletlerin karanlık arşivleri küresel dengeleri nasıl etkiler?",
        "options": ["Büyük bir uyanış yaratır / Awakening", "Dengeleri sarsar / Shakes balance", "Hiçbir şey değişmez / No change"]
    },
    {
        "question": "🚀 Yapay zeka ve uzay teknolojilerindeki bu hızla ilerleyen keşifler insanlığın sonunu mu getirecek, çağ mı atlatacak?",
        "options": ["Yeni bir çağ başlatır 🌟", "Tehlikeli bir son hazırlıyor ⚠️", "Kararsızım / Nötr 🤖"]
    },
    {
        "question": "🛰️ Sizce dünya dışı akıllı yaşam izleri hükümetler tarafından saklanıyor mu?",
        "options": ["Kesinlikle saklanıyor 👽", "Kesinlikle saklanmıyor 🌍", "Kanıt yok ama olabilir 🤔"]
    }
]

def send_telegram_message(text, reply_markup=None):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "HTML"}
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
        payload = {"chat_id": CHAT_ID, "photo": photo_url, "caption": caption, "parse_mode": "HTML"}
        if reply_markup:
            payload["reply_markup"] = json.dumps(reply_markup)
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"⚠️ Telegram Fotoğraf Gönderme Hatası: {e}")
    return None

def send_telegram_poll(question, options):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPoll"
        payload = {
            "chat_id": CHAT_ID,
            "question": question,
            "options": json.dumps(options),
            "is_anonymous": False
        }
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"⚠️ Telegram Anket Gönderme Hatası: {e}")
    return None

def check_live_news_and_intel():
    """Dünyadan anlık haber kokularını yakalayan gelişmiş tarayıcı"""
    try:
        feeds_shuffled = list(LIVE_RSS_FEEDS)
        random.shuffle(feeds_shuffled)
        
        for feed_url in feeds_shuffled:
            try:
                req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)
                    
                    # RSS veya Atom formatı kontrolü
                    items = []
                    channel = root.find('channel')
                    if channel is not None:
                        items = channel.findall('item')
                    else:
                        # Atom desteği
                        items = root.findall('{http://www.w3.org/2005/Atom}entry')

                    if items:
                        # En taze haberlerden rastgele birini seç
                        item = random.choice(items[:5])
                        
                        title_el = item.find('title') if channel is not None else item.find('{http://www.w3.org/2005/Atom}title')
                        link_el = item.find('link') if channel is not None else item.find('{http://www.w3.org/2005/Atom}link')
                        guid_el = item.find('guid') if channel is not None else item.find('{http://www.w3.org/2005/Atom}id')
                        
                        title = title_el.text if title_el is not None and title_el.text else "Küresel İstihbarat Akışı"
                        
                        # Link elementinin yapısına göre URL'yi çek
                        link = "https://t.me"
                        if link_el is not None:
                            link = link_el.text if link_el.text else link_el.get('href', "https://t.me")
                            
                        news_id = guid_el.text if guid_el is not None and guid_el.text else title
                        
                        if news_id not in sent_news_ids:
                            sent_news_ids.add(news_id)
                            if len(sent_news_ids) > 250:
                                sent_news_ids.pop()
                                
                            caption = (
                                f"⚡ <b>SINGULARITY ULTRA-CLASSIFIED INTEL</b>\n"
                                f"🏷️ <code>GLOBAL LIVE DISPATCH</code>\n\n"
                                f"🚨 <b>{title}</b>\n\n"
                                f"🇬🇧 <i>Live global intelligence wire</i>\n"
                                f"🇹🇷 <i>Canlı küresel istihbarat bülteni</i>\n\n"
                                f"📌 #BreakingNews #GlobalIntel #SingularityHub"
                            )
                            keyboard = {
                                "inline_keyboard": [[{"text": "🔗 Kaynak / Source", "url": link}]]
                            }
                            
                            send_telegram_message(caption, reply_markup=keyboard)
                            print(f"⚡ Canlı dünya haberi yakalandı ve fırlatıldı: {title}")
                            return True
            except Exception as inner_err:
                print(f"⚠️ Feed okuma alt hatası ({feed_url}): {inner_err}")
                continue
    except Exception as e:
        print(f"⚠️ Genel haber tarama hatası: {e}")
    return False

def background_scheduler():
    time.sleep(10)
    while True:
        try:
            # Her döngüde önce taze bir dünya haberi çekmeyi dene
            news_sent = check_live_news_and_intel()
            
            # Eğer haber çekilemediyse veya sıradaki turda arşiv/anket atılacaksa
            choice_type = random.choice(["post", "poll", "news_extra"])
            
            if choice_type == "post":
                available_posts = [p for p in ULTRA_CLASSIFIED_HUB if p['tag'] not in sent_archive_tags]
                if not available_posts:
                    sent_archive_tags.clear()
                    available_posts = ULTRA_CLASSIFIED_HUB
                    
                item = random.choice(available_posts)
                sent_archive_tags.append(item['tag'])
                
                caption = (
                    f"🌐 <b>SINGULARITY INTEL: ULTRA-CLASSIFIED ARCHIVES</b>\n"
                    f"🏷️ <code>{item['type']}</code>\n\n"
                    f"🇬🇧 <b>{item['title_en']}</b>\n"
                    f"🇹🇷 <b>{item['title_tr']}</b>\n\n"
                    f"🇬🇧 <i>{item['desc_en']}</i>\n"
                    f"🇹🇷 <i>{item['desc_tr']}</i>\n\n"
                    f"📌 #{item['tag']} #DeepWeb #SecretSatellites #SingularityHub"
                )
                keyboard = {
                    "inline_keyboard": [[{"text": "🔗 Gizli Dosyayı İncele / Source", "url": item['link']}]]
                }
                send_telegram_photo(item['image'], caption, reply_markup=keyboard)
                print("🌐 Arşiv postu fırlatıldı.")
                
            elif choice_type == "poll":
                poll = random.choice(POLL_POOL)
                send_telegram_poll(poll["question"], poll["options"])
                print("📊 Kanal anketi fırlatıldı.")
                
        except Exception as ex:
            print(f"Döngü hatası: {ex}")
            
        # Döngü hızı (her 30 saniyede bir yeni bir dünya kokusu veya arşiv patlatır)
        time.sleep(30)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 <b>Singularity Hub İstasyonu Tam Kapasite Devrede! (Canlı Dünya Haber Kokuları Aktif)</b>", parse_mode="HTML")

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item = random.choice(ULTRA_CLASSIFIED_HUB)
    caption = (
        f"🌐 <b>ULTRA-CLASSIFIED MANUAL DROP</b>\n\n"
        f"🇬🇧 {item['title_en']}\n"
        f"🇹🇷 {item['title_tr']}"
    )
    send_telegram_photo(item['image'], caption)
    await update.message.reply_text("🚀 Gizli dosya manuel olarak gruba çakıldı usta!")

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
    
    print(f"🚀 Canlı haber istasyonu aktif!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
