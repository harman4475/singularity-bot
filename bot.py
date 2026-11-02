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
    return "Singularity Hub Ultra-Classified Encyclopedia Station is active!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

def self_ping():
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "http://127.0.0.1:10000")
    while True:
        try:
            time.sleep(300)
            req = urllib.request.Request(render_url, headers={'User-Agent': 'KeepAliveBot'})
            with urllib.request.urlopen(req, timeout=10) as response:
                pass
        except Exception:
            pass

# ---------------------------------------------------------
# AYARLAR & KALICI HAFIZA DOSYASI
# ---------------------------------------------------------
BOT_TOKEN = "9068851091:AAFFpGSBNjJa3MlhtzeRiA3iKZ8aJ5ETWxE"
CHAT_ID = "-1004449764057"

HISTORY_FILE = "sent_news_history.json"
sent_archive_tags = []
sent_poll_ids = []

def load_sent_news():
    """Daha önce gönderilen haberleri ve içerikleri diskten yükler"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"⚠️ Geçmiş dosyası okunamadı: {e}")
    return set()

def save_sent_news(news_set):
    """Gönderilen içerikleri diske kaydeder"""
    try:
        data_list = list(news_set)[-2000:]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data_list, f)
    except Exception as e:
        print(f"⚠️ Geçmiş dosyasına yazılamadı: {e}")

sent_news_ids = load_sent_news()

# 🌐 KÜRESEL TEKNOLOJİ, SİBER GÜVENLİK VE UZAY ODAKLI DEV CANLI RSS AKIŞLARI
LIVE_RSS_FEEDS = [
    # Teknoloji & Yapay Zeka Odaklılar
    "https://www.technologyreview.com/feed/",
    "https://feeds.feedburner.com/VentureBeat",
    "https://arstechnica.com/feed/",
    "https://techcrunch.com/category/artificial-intelligence/feed/",
    # Siber Güvenlik & Hacker Dünyası
    "https://thehackernews.com/rss.xml",
    "https://www.darkreading.com/rss.xml",
    "https://www.bleepingcomputer.com/feed/",
    "https://krebsonsecurity.com/feed/",
    # Uzay, Bilim ve Kozmik Keşifler
    "https://www.space.com/home/feed/site.xml",
    "https://www.nasa.gov/news-release/feed/",
    "https://phys.org/rss-feed/",
    # Jeopolitik & Küresel Haberler
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.dw.com/rdf/rss-en-top"
]

# 🏛️ KÜRESEL TEKNOLOJİ, YAPAY ZEKA, SİBER GÜVENLİK, TELEGRAM VE FELSEFE ANSİKLOPEDİSİ (ULTRA_CLASSIFIED_HUB)
ULTRA_CLASSIFIED_HUB = [
    # --- 1. SÜPER GÜÇLERİN AR-GE VE SİLAH YARIŞI ---
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
        "type": "☢️ SUPERPOWER R&D & ADVANCED WEAPONS RACE",
        "title_en": "Classified Hypersonic Missiles and Next-Gen Electromagnetic Energy Weapons",
        "title_tr": "Sınıflandırılmış Hipersonik Füzeler ve Yeni Nesil Elektromanyetik Enerji Silahları",
        "desc_en": "Deep investigative breakdowns of global superpower defense labs and kinetic impactor prototypes.",
        "desc_tr": "Küresel süper güç savunma laboratuvarları ve kinetik çarpıştırıcı prototipleri hakkında derinlemesine incelemeler.",
        "image": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?q=80&w=1000&auto=format&fit=crop",
        "link": "https://www.nsa.gov",
        "tag": "BlackProjects"
    },
    {
        "type": "🇨🇳 CHINA'S QUANTUM & SPACE STATION INITIATIVES",
        "title_en": "Advanced Orbital Laser Arrays and Quantum Communication Encryption Grids",
        "title_tr": "Gelişmiş Yörünge Lazer Dizileri ve Kuantum İletişim Şifreleme Ağları",
        "desc_en": "Intelligence leaks regarding unhackable satellite data networks and high-energy atmospheric testing.",
        "desc_tr": "Hacklenemez uydu veri ağları ve yüksek enerjili atmosferik testler hakkındaki istihbarat sızıntıları.",
        "image": "https://images.unsplash.com/photo-1541185933-ef5d8ed016c2?q=80&w=1000&auto=format&fit=crop",
        "link": "https://english.www.gov.cn/",
        "tag": "ChinaTechGrid"
    },
    {
        "type": "🇺🇸 US DARPA COVERT INNOVATIONS & DEFENSE TECH",
        "title_en": "Experimental Directed-Energy Shielding and Telepathic Interface Helmets",
        "title_tr": "Deneysel Yönlendirilmiş Enerji Kalkanları ve Telepatik Arayüz Başlıkları",
        "desc_en": "Declassified documents on brain-computer interfacing for combat drone swarms.",
        "desc_tr": "Muharebe drone sürüleri için beyin-bilgisayar arayüzü üzerine gizliliği kaldırılmış belgeler.",
        "image": "https://images.unsplash.com/photo-1508614589041-895b88991e3e?q=80&w=1000&auto=format&fit=crop",
        "link": "https://www.darpa.mil/",
        "tag": "DARPABreakthroughs"
    },

    # --- 2. YAPAY ZEKA MODELLERİ VE UZMANLIK ALANLARI ---
    {
        "type": "🤖 AI SUPERINTELLIGENCE & LLM ECOSYSTEM",
        "title_en": "The Hidden Specialization Map of World's Top AI Models: GPT, Claude, and Llama",
        "title_tr": "Dünyanın En İyi Yapay Zeka Modellerinin Gizli Uzmanlık Haritası: GPT, Claude ve Llama",
        "desc_en": "Detailed analysis of which AI model excels at logic, deep coding, creative writing, or local security.",
        "desc_tr": "Hangi yapay zeka modelinin mantık, derin kodlama, yaratıcı yazım veya yerel güvenlikte öne çıktığının detaylı analizi.",
        "image": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?q=80&w=1000&auto=format&fit=crop",
        "link": "https://openai.com/research",
        "tag": "AIModelsMap"
    },
    {
        "type": "🧬 SCIENTIFIC & BIOLOGICAL AI REVOLUTION",
        "title_en": "AlphaFold & GNoME: How AI is Decoding Protein Folding and Discovering New Materials",
        "title_tr": "AlphaFold & GNoME: Yapay Zeka Protein Katlamasını Nasıl Çözüyor ve Yeni Malzemeler Keşfediyor?",
        "desc_en": "Breakthrough computational biology systems rewriting medicine and molecular engineering.",
        "desc_tr": "Tıbbı ve moleküler mühendisliği yeniden yazan çığır açıcı hesaplamalı biyoloji sistemleri.",
        "image": "https://images.unsplash.com/photo-1507413245164-6160d8298b31?q=80&w=1000&auto=format&fit=crop",
        "link": "https://deepmind.google/science/",
        "tag": "ScientificAI"
    },
    {
        "type": "🎨 GENERATIVE MEDIA & VIDEO SYNTHESIS",
        "title_en": "Sora, Midjourney v6 and Flux: The Cinematic Reality Engine Matrix",
        "title_tr": "Sora, Midjourney v6 ve Flux: Sinematik Gerçeklik Motoru Matrisi",
        "desc_en": "Technical breakdown of latent space diffusion models producing hyper-realistic visual media.",
        "desc_tr": "Hiper-gerçekçi görsel medya üreten latent uzay difüzyon modellerinin teknik incelemesi.",
        "image": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=1000&auto=format&fit=crop",
        "link": "https://stability.ai/",
        "tag": "GenerativeMedia"
    },

    # --- 3. SİBER GÜVENLİK, HACKER DÜNYASI VE "ZERO-DAY" ---
    {
        "type": "🗂️ DEEP WEB ARCHIVES & CLANDESTINE STATE SECRETS",
        "title_en": "Leaked Underground Dossiers: Zero-Day Exploits and Hidden Cyber Warfare",
        "title_tr": "Sızdırılan Yeraltı Dosyaları: Sıfırıncı Gün Açıkları ve Gizli Siber Savaşlar",
        "desc_en": "Unfiltered data dumps from deep web network nodes revealing covert network attacks.",
        "desc_tr": "Gizli ağ saldırılarını ifşa eden deep web ağ düğümlerinden filtrelenmemiş veri dökümleri.",
        "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1000&auto=format&fit=crop",
        "link": "https://anonymouse.org",
        "tag": "DeepWebFiles"
    },
    {
        "type": "🛡️ POST-QUANTUM CRYPTOGRAPHY & SECURITY",
        "title_en": "Securing Digital Infrastructure Against Future Quantum Computing Decryption",
        "title_tr": "Gelecekteki Kuantum Bilgisayar Şifre Çözücülerine Karşı Dijital Altyapıyı Güvenceye Almak",
        "desc_en": "Advanced lattice-based cryptographic protocols designed to resist quantum brute-force attacks.",
        "desc_tr": "Kuantum kaba kuvvet saldırılarına direnmek için tasarlanmış gelişmiş kafes tabanlı kriptografik protokoller.",
        "image": "https://images.unsplash.com/photo-1563986768609-322da13575f3?q=80&w=1000&auto=format&fit=crop",
        "link": "https://csrc.nist.gov/",
        "tag": "QuantumCrypto"
    },

    # --- 4. HERKESİN BİLMEDİĞİ GİZLİ TAKTİKLER & "NASIL YAPILIR?" ---
    {
        "type": "🕵️ ADVANCED OSINT & DIGITAL GHOST TACTICS",
        "title_en": "The Professional Guide to Leaving Zero Digital Footprint and EXIF Scrubbing",
        "title_tr": "Sıfır Dijital İz Bırakma ve EXIF Verisi Temizleme Üzerine Profesyonel Rehber",
        "desc_en": "Hidden techniques used by intelligence operatives to erase metadata and bypass browser fingerprinting.",
        "desc_tr": "İstihbarat ajanlarının meta verileri silmek ve tarayıcı parmak izini atlatmak için kullandığı gizli teknikler.",
        "image": "https://images.unsplash.com/photo-1510519138161-5364d8cd7bbbc?q=80&w=1000&auto=format&fit=crop",
        "link": "https://www.bellingcat.com/",
        "tag": "OSINTSecrets"
    },
    {
        "type": "⚡ LOCAL LLM & PRIVATE HACKER ENVIRONMENTS",
        "title_en": "How to Run Offline, Unrestricted Open-Source AI Models on Local Hardware",
        "title_tr": "Yerel Donanımda Çevrimdışı ve Kısıtlamasız Açık Kaynaklı Yapay Zeka Modelleri Nasıl Çalıştırılır?",
        "desc_en": "Step-by-step masterclass on setting up private quantized models without sending data to cloud servers.",
        "desc_tr": "Bulut sunuculara veri göndermeden özel kuantize modeller kurma konusunda adım adım ustalık sınıfı.",
        "image": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1000&auto=format&fit=crop",
        "link": "https://ollama.com/",
        "tag": "LocalAIHacks"
    },

    # --- 5. TELEGRAM'IN GİZLİ ÖZELLİKLERİ VE BİLİNMEYENLERİ ---
    {
        "type": "📱 TELEGRAM DEEP SECRETS & CLOUD STORAGE HACKS",
        "title_en": "Unlocking Telegram's Hidden Cloud Powerhouse and Secret Chat Protocols",
        "title_tr": "Telegram'ın Gizli Bulut Gücünü ve Gizli Sohbet Protokollerini Keşfetmek",
        "desc_en": "Advanced tips on using saved messages as infinite secure storage and bypassing deep network restrictions.",
        "desc_tr": "Kayıtlı mesajları sonsuz güvenli depolama alanı olarak kullanma ve derin ağ kısıtlamalarını aşma üzerine ipuçları.",
        "image": "https://images.unsplash.com/photo-1611746872915-64382b5c76da?q=80&w=1000&auto=format&fit=crop",
        "link": "https://telegram.org/faq",
        "tag": "TelegramSecrets"
    },

    # --- 6. KOZMİK SORULAR VE FELSEFİ DERİNLİK ---
    {
        "type": "🧠 THE MYSTERY OF CONSCIOUSNESS & SELF",
        "title_en": "The Hard Problem of Consciousness: How Do Neurons Create Subjective Experience?",
        "title_tr": "Bilincin Zor Problemi: Nöronlar Öznel Deneyimi Nasıl Yaratıyor?",
        "desc_en": "Philosophical and neurological deep dive into why matter wakes up and experiences reality.",
        "desc_tr": "Maddenin nasıl uyanıp gerçekliği deneyimlediğine dair felsefi ve nörolojik derin dalış.",
        "image": "https://images.unsplash.com/photo-1507668077129-56e32842fceb?q=80&w=1000&auto=format&fit=crop",
        "link": "https://plato.stanford.edu/entries/consciousness/",
        "tag": "PhilosophyOfMind"
    },
    {
        "type": "⏳ THE NATURE OF TIME & ILLUSION",
        "title_en": "Is Time an Illusion? Einstein's Block Universe and the Eternal Now",
        "title_tr": "Zaman Bir İllüzyon mu? Einstein'ın Blok Evreni ve Ebedi Şimdi",
        "desc_en": "Exploring relativity theories suggesting past, present, and future coexist simultaneously in the cosmic fabric.",
        "desc_tr": "Geçmişin, şimdinin ve geleceğin kozmik kumaşta aynı anda var olduğunu öne süren görelilik teorilerini keşfetmek.",
        "image": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?q=80&w=1000&auto=format&fit=crop",
        "link": "https://www.space.com",
        "tag": "TimeIllusion"
    },
    {
        "type": "🌌 ORIGIN OF THE UNIVERSE & THE GREAT VOID",
        "title_en": "Before the Big Bang: Why Is There Something Rather Than Nothing?",
        "title_tr": "Büyük Patlama'dan Önce: Neden Hiçlik Yerine Bir Şeyler Var?",
        "desc_en": "Cosmological inquiries into absolute nothingness, multiverses, and the birth of space-time dimensions.",
        "desc_tr": "Mutlak hiçliğe, çoklu evrenlere ve uzay-zaman boyutlarının doğumuna dair kozmolojik sorgulamalar.",
        "image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=1000&auto=format&fit=crop",
        "link": "https://home.cern/",
        "tag": "CosmicOrigins"
    }
]

# 📊 ZENGİNLEŞTİRİLMİŞ İNTERAKTİF ANKET HAVUZU (SOSYAL, KİŞİLİK, SEKTÖREL VE TEKNOLOJİK)
POLL_POOL = [
    # Yapay Zeka & Teknoloji Oylamaları
    {
        "id": "poll_ai_1", 
        "question": "🤖 Gelecekte tüm meslekleri eline alacak yapay zeka sence insanlık için en büyük tehdit mi, yoksa kurtuluş mu?\n🇬🇧 Is AI taking over all jobs the greatest threat or salvation for humanity?", 
        "options": ["Büyük bir kurtuluş / Salvation", "Varoluşsal büyük tehdit / Massive threat", "Dengeli bir geçiş / Balanced transition"]
    },
    {
        "id": "poll_ai_2", 
        "question": "🧠 Sence hangi yapay zeka modeli günlük hayatta senin en büyük yardımcın?\n🇬🇧 Which AI model is your ultimate daily assistant?", 
        "options": ["GPT-4o / OpenAI", "Claude 3.5 / Anthropic", "Llama / Açık Kaynak (Open Source)", "Hiçbiri / None"]
    },
    # Kararsızlık & "Would You Rather" Anketleri
    {
        "id": "poll_choice_1", 
        "question": "🌐 Tercih yapman gerekseydi: Ömür boyu internetten tamamen kopmak mı, yoksa sadece yer altındaki sığınaklarda yaşamak mı?\n🇬🇧 Would you rather disconnect from the internet forever or live underground bunkers?", 
        "options": ["İnternetsiz bir ömür / No internet", "Yeraltı sığınakları / Underground life", "İkisi de imkansız / Both impossible"]
    },
    {
        "id": "poll_choice_2", 
        "question": "🕵️ Dijital dünyada seçimin: Sınırsız dijital gizlilik ve görünmezlik mi, yoksa tüm teknolojik güce ve bilgilere anında erişim mi?\n🇬🇧 Your digital choice: Total invisible privacy or instant access to all global tech power?", 
        "options": ["Mutlak gizlilik / Absolute privacy", "Mutlak güç ve bilgi / Absolute power", "Kararsızım / Undecided"]
    },
    # Kişilik & Karakter Testi Tarzı Oylamalar
    {
        "id": "poll_personality_1", 
        "question": "🧩 Karakter analizine göre kendini en çok hangi teknoloji grubunda görüyorsun?\n🇬🇧 According to your personality, which tech group do you belong to?", 
        "options": ["Siber Güvenlik / Hacker", "Yapay Zeka Mimarı / AI Builder", "Kozmik Felsefe / Deep Thinker", "Sessiz Gözlemci / Observer"]
    },
    # Sektörel & Küresel Eğilim Anketleri
    {
        "id": "poll_global_1", 
        "question": "🚀 Sence insanlığın bu yüzyılda başardığı en devrimci teknolojik sıçrama hangisiydi?\n🇬🇧 What was humanity's most revolutionary technological leap this century?", 
        "options": ["Yapay Zeka / AI & AGI", "Kuantum Bilgisayarlar / Quantum", "Uzay Keşifleri / Space Travel", "Genom / CRISPR Biyoteknoloji"]
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
    try:
        feeds_shuffled = list(LIVE_RSS_FEEDS)
        random.shuffle(feeds_shuffled)
        
        for feed_url in feeds_shuffled:
            try:
                req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(req, timeout=10) as response:
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)
                    
                    items = []
                    channel = root.find('channel')
                    if channel is not None:
                        items = channel.findall('item')
                    else:
                        items = root.findall('{http://www.w3.org/2005/Atom}entry')

                    if items:
                        random.shuffle(items)
                        for item in items[:15]:
                            title_el = item.find('title') if channel is not None else item.find('{http://www.w3.org/2005/Atom}title')
                            link_el = item.find('link') if channel is not None else item.find('{http://www.w3.org/2005/Atom}link')
                            guid_el = item.find('guid') if channel is not None else item.find('{http://www.w3.org/2005/Atom}id')
                            
                            title = title_el.text if title_el is not None and title_el.text else "Küresel İstihbarat Akışı"
                            link = "https://t.me"
                            if link_el is not None:
                                link = link_el.text if link_el.text else link_el.get('href', "https://t.me")
                                
                            news_id = guid_el.text if (guid_el is not None and guid_el.text) else (link if link != "https://t.me" else title)
                            
                            if news_id not in sent_news_ids:
                                sent_news_ids.add(news_id)
                                save_sent_news(sent_news_ids)
                                
                                caption = (
                                    f"⚡ <b>SINGULARITY ULTRA-CLASSIFIED INTEL</b>\n"
                                    f"🏷️ <code>GLOBAL TECH & CYBER WIRE</code>\n\n"
                                    f"🚨 <b>{title}</b>\n\n"
                                    f"🇬🇧 <i>Live intelligence dispatch</i>\n"
                                    f"🇹🇷 <i>Canlı teknoloji ve siber bülten</i>\n\n"
                                    f"📌 #TechNews #CyberSecurity #SingularityHub"
                                )
                                keyboard = {
                                    "inline_keyboard": [[{"text": "🔗 Kaynak / Source", "url": link}]]
                                }
                                
                                send_telegram_message(caption, reply_markup=keyboard)
                                print(f"⚡ Canlı teknoloji/siber haberi yakalandı ve fırlatıldı: {title}")
                                return True
            except Exception as inner_err:
                continue
    except Exception as e:
        print(f"⚠️ Genel haber tarama hatası: {e}")
    return False

def background_scheduler():
    time.sleep(15)
    while True:
        try:
            choice_type = random.choice(["post", "poll", "news"])
            
            if choice_type == "news":
                success = check_live_news_and_intel()
                if not success:
                    choice_type = "post"
            
            if choice_type == "post":
                available_posts = [p for p in ULTRA_CLASSIFIED_HUB if p['tag'] not in sent_archive_tags]
                if not available_posts:
                    sent_archive_tags.clear()
                    available_posts = ULTRA_CLASSIFIED_HUB
                    
                item = random.choice(available_posts)
                sent_archive_tags.append(item['tag'])
                
                caption = (
                    f"🌐 <b>SINGULARITY ENCYCLOPEDIA HUB</b>\n"
                    f"🏷️ <code>{item['type']}</code>\n\n"
                    f"🇬🇧 <b>{item['title_en']}</b>\n"
                    f"🇹🇷 <b>{item['title_tr']}</b>\n\n"
                    f"🇬🇧 <i>{item['desc_en']}</i>\n"
                    f"🇹🇷 <i>{item['desc_tr']}</i>\n\n"
                    f"📌 #{item['tag']} #DeepTech #SingularityHub"
                )
                keyboard = {
                    "inline_keyboard": [[{"text": "🔗 Detaylı İncele / Source", "url": item['link']}]]
                }
                send_telegram_photo(item['image'], caption, reply_markup=keyboard)
                print("🌐 Ansiklopedi arşivi postu fırlatıldı.")
                
            elif choice_type == "poll":
                available_polls = [p for p in POLL_POOL if p['id'] not in sent_poll_ids]
                if not available_polls:
                    sent_poll_ids.clear()
                    available_polls = POLL_POOL
                    
                poll = random.choice(available_polls)
                sent_poll_ids.append(poll['id'])
                
                send_telegram_poll(poll["question"], poll["options"])
                print("📊 İnteraktif anket fırlatıldı.")
                
        except Exception as ex:
            print(f"Döngü hatası: {ex}")
            
        time.sleep(3600)  # Paylaşım aralığı

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 <b>Singularity Hub İstasyonu Ansiklopedi Modunda Tam Kapasite Devrede!</b>", parse_mode="HTML")

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    item = random.choice(ULTRA_CLASSIFIED_HUB)
    caption = (
        f"🌐 <b>ULTRA-CLASSIFIED MANUAL DROP</b>\n\n"
        f"🇬🇧 {item['title_en']}\n"
        f"🇹🇷 {item['title_tr']}"
    )
    send_telegram_photo(item['image'], caption)
    await update.message.reply_text("🚀 Ansiklopedi kartı manuel olarak gruba çakıldı usta!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("post", post_command))
    
    # 1. Mini Web Sunucusu (Render Health-Check için)
    t_web = threading.Thread(target=run_web)
    t_web.daemon = True
    t_web.start()
    
    # 2. Keep-Alive Ping İş Parçacığı
    t_ping = threading.Thread(target=self_ping)
    t_ping.daemon = True
    t_ping.start()

    # 3. Arka Plan Paylaşım Döngüsü
    t_sched = threading.Thread(target=background_scheduler)
    t_sched.daemon = True
    t_sched.start()
    
    print(f"🚀 Singularity Ansiklopedi İstasyonu aktif!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
