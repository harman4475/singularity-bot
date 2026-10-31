import logging
import random
import os
import urllib.request
import xml.etree.ElementTree as ET
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, JobQueue

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

# 🕵️ KİMSENİN BİLMEDİĞİ GİZLİ UYDULAR, DEEP WEB VE SANSÜRSÜZ İSTİHBARAT HAVUZU (8 DİL)
ULTRA_CLASSIFIED_HUB = [
    {
        "type": "🛰️ SECRET SATELLITES & OMNISCIENT ORBITS / SATELLITES ESPIONS",
        "title_en": "Unknown Military Spy Satellites Tracking Every Move on Earth",
        "title_tr": "Dünya Üzerindeki Her Hareketi İzleyen Gizli Askeri Casus Uydular ve Kör Noktalar",
        "title_de": "Unbekannte militärische Spionagesatelliten überwachen jede Bewegung",
        "title_es": "Satélites espías militares desconocidos que rastrean cada movimiento",
        "title_it": "Satelliti spia militari sconosciuti che tracciano ogni movimento",
        "title_hi": "गुप्त सैन्य जासूस उपग्रह पृथ्वी पर हर गति पर नजर रख रहे हैं",
        "desc_en": "Deep background intelligence on black-budget orbital assets capable of sub-meter ground resolution and encrypted signal interception.",
        "desc_tr": "Alt-metre zemin çözünürlüğüne ve şifreli sinyal ele geçirme yeteneğine sahip gizli bütçeli yörünge varlıkları hakkında derin arka plan.",
        "image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1000&auto=format&fit=crop",
        "link": "https://nsarchive.gwu.edu/",
        "tag": "SecretSatellites"
    },
    {
        "type": "🗂️ DEEP WEB ARCHIVES & CLANDESTINE STATE SECRETS / ARCHIVES SECRÈTES",
        "title_en": "Leaked Underground Dossiers: The Truth Governments Hide from Public",
        "title_tr": "Sızdırılan Yeraltı Dosyaları: Hükümetlerin Halktan Sakladığı Gerçekler",
        "title_de": "Durchgesickerte Untergrund-Dossiers: Die Wahrheit der Regierungen",
        "title_es": "Dosieres subterráneos filtrados: La verdad que los gobiernos ocultan",
        "title_it": "Dossier sotterranei泄露: La verità che i governi nascondono",
        "title_hi": "लीक हुए भूमिगत Dossiers: सरकारों द्वारा छिपाए गए सत्य",
        "desc_en": "Unfiltered data dumps from deep web network nodes revealing covert government research, forgotten treaties, and underground facilities.",
        "desc_tr": "Gizli hükümet araştırmalarını, unutulmuş anlaşmaları ve yeraltı tesislerini ifşa eden deep web ağ düğümlerinden filtrelenmemiş veri sızıntıları.",
        "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1000&auto=format&fit=crop",
        "link": "https://anonymouse.org",
        "tag": "DeepWebFiles"
    },
    {
        "type": "☢️ UNKNOWN WEAPONS R&D & BLACK PROJECTS / PROJETS NOIRS",
        "title_en": "Classified Electromagnetic Energy Weapons and Underground R&D Labs",
        "title_tr": "Sınıflandırılmış Elektromanyetik Enerji Silahları ve Gizli Yeraltı Ar-Ge Laboratuvarları",
        "title_de": "Klassifizierte elektromagnetische Energiewaffen & unterirdische Labore",
        "title_es": "Armas de energía electromagnética clasificadas y laboratorios subterráneos",
        "title_it": "Armi ad energia elettromagnetica classificate e laboratori sotterranei",
        "title_hi": "वर्गीकृत विद्युत चुम्बकीय ऊर्जा हथियार और भूमिगत अनुसंधान प्रयोगशालाएं",
        "desc_en": "Deep investigative breakdowns of kinetic impactors, directed-energy prototypes, and classified military complexes.",
        "desc_tr": "Kinetik çarpıştırıcılar, yönlendirilmiş enerji prototipleri ve sınıflandırılmış askeri kompleksler hakkında derinlemesine incelemeler.",
        "image": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?q=80&w=1000&auto=format&fit=crop",
        "link": "https://www.nsa.gov",
        "tag": "BlackProjects"
    }
]

POLL_POOL = [
    {
        "question": "🌐 Sizce uzaydaki gizli askeri casus uydular halktan daha başka ne kadar saklanabilir?",
        "options": ["Çoktan ifşa oldu / Already exposed", "Hâlâ tamamen gizli / Fully secret", "Bilinmiyor / Unknown"]
    },
    {
        "question": "🕵️ Deep web sızıntıları ve devletlerin karanlık arşivleri dünyayı nasıl etkiler?",
        "options": ["Küresel uyanıș yaratır / Awakening", "Dengeleri sarsar / Shakes balance", "Hiçbir şey değişmez / No change"]
    }
]

# ---------------------------------------------------------
# PERİYODİK GÖREVLER (TELEGRAM JOB QUEUE)
# ---------------------------------------------------------
async def check_live_news_job(context: ContextTypes.DEFAULT_TYPE):
    """Her 30 saniyede bir çalışıp RSS beslemelerini kontrol eder."""
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
                                "⚡ <b>SINGULARITY ULTRA-CLASSIFIED INTEL</b>\n"
                                "🏷️ <code>REAL-TIME FEED ALERT</code>\n\n"
                                f"🚨 <b>{title}</b>\n\n"
                                "🇬🇧 <i>Unfiltered global intelligence feed</i>\n"
                                "🇹🇷 <i>Filtrelenmemiş küresel istihbarat akışı</i>\n"
                                "🇩🇪 <i>Ungefilterter globaler Feed</i>\n"
                                "🇪🇸 <i>Flujo de inteligencia sin filtrar</i>\n"
                                "🇮🇹 <i>Feed di intelligence non filtrato</i>\n"
                                "🇮🇳 <i>फिल्टर न किया गया वैश्विक फ़ीड</i>\n\n"
                                "📌 #BreakingNews #SecretSatellites #SingularityHub"
                            )
                            keyboard = [[InlineKeyboardButton("🔗 Kaynak / Source / Quelle", url=link)]]
                            
                            await context.bot.send_message(
                                chat_id=CHAT_ID,
                                text=caption,
                                parse_mode="HTML",
                                reply_markup=InlineKeyboardMarkup(keyboard)
                            )
                            print(f"⚡ Gizli akış haberi fırlatıldı: {title}")
                            return
    except Exception as e:
        print(f"⚠️ Haber tarama hatası: {e}")

async def periodic_archives_job(context: ContextTypes.DEFAULT_TYPE):
    """Her 10 dakikada bir çalışıp rastgele arşiv postası veya anket atar."""
    try:
        choice_type = random.choice(["post", "poll"])
        if choice_type == "post":
            item = random.choice(ULTRA_CLASSIFIED_HUB)
            caption = (
                f"🌐 <b>SINGULARITY INTEL: ULTRA-CLASSIFIED ARCHIVES</b>\n"
                f"🏷️ <code>{item['type']}</code>\n\n"
                f"🇬🇧 <b>{item['title_en']}</b>\n"
                f"🇹🇷 <b>{item['title_tr']}</b>\n"
                f"🇩🇪 <b>{item['title_de']}</b>\n"
                f"🇪🇸 <b>{item['title_es']}</b>\n"
                f"🇮🇹 <b>{item['title_it']}</b>\n"
                f"🇮🇳 <b>{item['title_hi']}</b>\n\n"
                f"🇬🇧 <i>{item['desc_en']}</i>\n"
                f"🇹🇷 <i>{item['desc_tr']}</i>\n\n"
                f"📌 #{item['tag']} #DeepWeb #SecretSatellites #SingularityHub"
            )
            keyboard = [[InlineKeyboardButton("🔗 Gizli Dosyayı İncele / Source", url=item['link'])]]
            await context.bot.send_photo(
                chat_id=CHAT_ID, 
                photo=item['image'], 
                caption=caption, 
                parse_mode="HTML", 
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            print("🌐 Periyodik arşiv postası fırlatıldı!")
        else:
            poll = random.choice(POLL_POOL)
            await context.bot.send_poll(
                chat_id=CHAT_ID, 
                question=poll["question"], 
                options=poll["options"], 
                is_anonymous=False
            )
            print("📊 Periyodik anket fırlatıldı!")
    except Exception as ex:
        print(f"⚠️ Arşiv/Anket görev hatası: {ex}")

# ---------------------------------------------------------
# KOMUTLAR
# ---------------------------------------------------------
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 <b>Ultra-Classified Station Aktif!</b> Gizli uydular ve yeraltı arşivleri devrede.", parse_mode="HTML")

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bot = context.bot
    item = random.choice(ULTRA_CLASSIFIED_HUB)
    caption = (
        f"🌐 <b>ULTRA-CLASSIFIED MANUAL DROP</b>\n\n"
        f"🇬🇧 {item['title_en']}\n"
        f"🇹🇷 {item['title_tr']}\n"
        f"🇩🇪 {item['title_de']}\n"
        f"🇪🇸 {item['title_es']}\n"
        f"🇮🇹 {item['title_it']}\n"
        f"🇮🇳 {item['title_hi']}"
    )
    await bot.send_photo(chat_id=CHAT_ID, photo=item['image'], caption=caption, parse_mode="HTML")
    await update.message.reply_text("🚀 Kimsenin bilmediği gizli dosyalar manuel olarak çakıldı usta!")

def main():
    # Flask sunucusunu arka planda başlat (Keep-alive)
    import threading
    t_web = threading.Thread(target=run_web)
    t_web.daemon = True
    t_web.start()

    # Telegram Bot Uygulamasını Kur
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Komut Handler'ları
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("post", post_command))
    
    # Job Queue (Zamanlayıcı) Entegrasyonu
    job_queue = app.job_queue
    # Her 30 saniyede bir RSS haberlerini kontrol et
    job_queue.run_repeating(check_live_news_job, interval=30, first=10)
    # Her 600 saniyede (10 dakikada) bir arşiv/anket at
    job_queue.run_repeating(periodic_archives_job, interval=600, first=20)

    print(f"🚀 Ultra-Classified Station devrede ve JobQueue aktif!")
    
    # Botu çalıştır
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
