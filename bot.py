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
# AYARLAR & KALICI HAFIZA DOSYASI
# ---------------------------------------------------------
BOT_TOKEN = "9068851091:AAFFpGSBNjJa3MlhtzeRiA3iKZ8aJ5ETWxE"
CHAT_ID = "-1004449764057"

HISTORY_FILE = "sent_news_history.json"
sent_archive_tags = []
sent_poll_ids = []  # Atılan anketlerin tekrar etmemesi için hafıza

def load_sent_news():
    """Daha önce gönderilen haberleri diskten yükler (Restart'ta unutmaz)"""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"⚠️ Geçmiş dosyası okunamadı: {e}")
    return set()

def save_sent_news(news_set):
    """Gönderilen haberleri diske kaydeder"""
    try:
        data_list = list(news_set)[-1500:]
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data_list, f)
    except Exception as e:
        print(f"⚠️ Geçmiş dosyasına yazılamadı: {e}")

sent_news_ids = load_sent_news()

# 🌐 DÜNYANIN DÖRT BİR YANINDAN ENTEGRE VE CANLI HABER AKIŞLARI
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

# 📊 KANAL İÇİN DEVASA VE ZENGİNLEŞTİRİLMİŞ ÇOK DİLLİ ANKET HAVUZU (50 ADET)
POLL_POOL = [
    {"id": "poll_1", "question": "🌐 Gizli askeri uydular halktan daha ne kadar saklanabilir?\n🇬🇧 How long can secret military satellites be hidden?", "options": ["Çoktan ifşa oldu / Already exposed", "Hâlâ tamamen gizli / Fully secret", "Bilinmiyor / Unknown"]},
    {"id": "poll_2", "question": "🕵️ Deep web sızıntıları küresel dengeleri nasıl etkiler?\n🇬🇧 How do deep web leaks affect global balance?", "options": ["Büyük bir uyanış / Awakening", "Dengeleri sarsar / Shakes balance", "Hiçbir şey değişmez / No change"]},
    {"id": "poll_3", "question": "🚀 Yapay zeka ve uzay keşifleri insanlığın sonunu mu getirecek, çağ mı atlatacak?\n🇬🇧 Will AI and space discoveries end humanity or start a new era?", "options": ["Yeni bir çağ / New era 🌟", "Tehlikeli bir son / Dangerous end ⚠️", "Kararsızım / Neutral 🤖"]},
    {"id": "poll_4", "question": "🛰️ Dünya dışı akıllı yaşam hükümetler tarafından saklanıyor mu?\n🇬🇧 Is extraterrestrial life hidden by governments?", "options": ["Kesinlikle saklanıyor / Yes 👽", "Saklanmıyor / No 🌍", "Kanıt yok / Maybe 🤔"]},
    {"id": "poll_5", "question": "🧠 Yapay zeka bilinç kazanırsa insanlık için en büyük tehdit ne olur?\n🇬🇧 If AI gains consciousness, what will be the biggest threat?", "options": ["Kontrolün kaybı / Loss of control", "Ekonomik çöküş / Economic collapse", "Tehdit yok / No threat"]},
    {"id": "poll_6", "question": "⏳ Zaman yolculuğu gelecekte fiziksel olarak mümkün olacak mı?\n🇬🇧 Will physical time travel be possible in the future?", "options": ["Kesinlikle evet / Absolutely yes", "Asla mümkün değil / Never", "Sadece kuantum düzeyde / Only quantum level"]},
    {"id": "poll_7", "question": "🌌 Evrende yalnız mıyız, yoksa galaktik bir medeniyetler federasyonu var mı?\n🇬🇧 Are we alone in the universe, or is there a galactic federation?", "options": ["Yalnızız / We are alone", "Federasyon var / Federation exists", "Bize karışmıyorlar / They avoid us"]},
    {"id": "poll_8", "question": "💡 Küresel internet altyapısı tek bir tuşla tamamen çöktürülebilir mi?\n🇬🇧 Can the global internet infrastructure be completely collapsed with a single switch?", "options": ["Evet, çok kırılgan / Very fragile", "Asla çökmez / Impossible", "Kısmen kesilebilir / Partially"]},
    {"id": "poll_9", "question": "🔬 Yeraltı kuantum laboratuvarlarında paralel evrenlere geçiş denendi mi?\n🇬🇧 Have parallel universe crossings been tested in underground quantum labs?", "options": ["Kesinlikle denendi / Tested", "Sadece teori / Only theory", "Büyük bir yalan / A big lie"]},
    {"id": "poll_10", "question": "👁️ Dijital gözetim ve yüz tanıma sistemleri bireysel özgürlüğü bitirdi mi?\n🇬🇧 Has digital surveillance ended individual freedom?", "options": ["Evet, bitti / Yes, ended", "Hâlâ direniyoruz / Still resisting", "Farkında değiliz / Unaware"]},
    {"id": "poll_11", "question": "⚡ Kablosuz enerji ve Tesla'nın kayıp buluşları gizlice kullanılıyor mu?\n🇬🇧 Are wireless energy and Tesla's lost inventions secretly in use?", "options": ["Gizlice kullanılıyor / Used secretly", "Tamamen masal / Pure fairy tale", "Araştırılıyor / Under research"]},
    {"id": "poll_12", "question": "🧬 İnsan DNA'sına müdahale edilerek geleceğin süper insanları üretiliyor mu?\n🇬🇧 Are future super-humans being created by interfering with human DNA?", "options": ["Gizli tesislerde evet / Yes in secret labs", "Henüz erken / Too early", "İmkansız / Impossible"]},
    {"id": "poll_13", "question": "🛸 Okyanusların en derin çukurlarında insan yapımı gizli üsler var mı?\n🇬🇧 Are there man-made secret bases in the deepest ocean trenches?", "options": ["Kesinlikle var / Absolutely yes", "Sadece doğal yaşam / Marine life", "Bilinmiyor / Unknown"]},
    {"id": "poll_14", "question": "🔮 Süper zeka (AGI) insanlığı yönetmeye başlarsa adil bir düzen kurabilir mi?\n🇬🇧 Can AGI establish a fair order if it starts managing humanity?", "options": ["Mükemmel adalet / Perfect justice", "Diktatörlük / Tyranny", "İnsanlığı siler / Eradicate humanity"]},
    {"id": "poll_15", "question": "🛡️ Küresel siber savaşlar nükleer savaşlardan daha büyük bir tehlike mi?\n🇬🇧 Are global cyber wars a bigger threat than nuclear wars?", "options": ["Kesinlikle daha büyük / Definitely bigger", "Nükleer daha tehlikeli / Nuclear is worse", "Eşdeğer / Equal threat"]},
    {"id": "poll_16", "question": "🤖 Robotlar gelecekte duygusal kararlar alabilir mi?\n🇬🇧 Will robots be able to make emotional decisions in the future?", "options": ["Evet, simüle eder / Yes, simulated", "Asla hissedemez / Never feel", "Bilinç kazanırlar / Will gain consciousness"]},
    {"id": "poll_17", "question": "🌋 Süper yanardağ patlamaları küresel uygarlığı yok edebilir mi?\n🇬🇧 Can supervolcano eruptions destroy global civilization?", "options": ["Evet, büyük tehlike / Huge danger", "Teknoloji kurtarır / Technology saves", "Düşük ihtimal / Low probability"]},
    {"id": "poll_18", "question": "🌑 Ay'ın karanlık yüzünde gizli insan üsleri olduğu iddiaları gerçek mi?\n🇬🇧 Are claims of secret human bases on the dark side of the Moon true?", "options": ["Kesinlikle gerçek / Absolutely true", "Tamamen komplo / Pure conspiracy", "Gizli ortak üs var / Joint base"]},
    {"id": "poll_19", "question": "🧊 Kutuplardaki buzulların altında antik uygarlıklara ait kalıntılar çıkıyor mu?\n🇬🇧 Are relics of ancient civilizations emerging from beneath polar ice?", "options": ["Evet, saklıyorlar / Yes, hidden", "Sadece bakteri / Only bacteria", "Bilimsel spekülasyon / Speculation"]},
    {"id": "poll_20", "question": "🔋 Lityum pillerin yerini alacak nihai enerji kaynağı ne zaman bulunur?\n🇬🇧 When will the ultimate energy source replacing lithium batteries be found?", "options": ["Çok yakın / Very soon", "On yıllar sonra / Decades later", "Mümkün değil / Impossible"]},
    {"id": "poll_21", "question": "🛰️ Alçak yörünge uydu ağları (Starlink vb.) gece gökyüzünü ve astronomiyi bitiriyor mu?\n🇬🇧 Are low Earth orbit satellite networks destroying night sky astronomy?", "options": ["Evet, büyük tehdit / Big threat", "Zararsız / Harmless", "Alternatif çözümler bulunur / Solutions found"]},
    {"id": "poll_22", "question": "🧬 Genetik silâhlar gelecekte belirli etnik grupları hedef alabilir mi?\n🇬🇧 Can genetic weapons target specific ethnic groups in the future?", "options": ["Teknik olarak mümkün / Technically possible", "Uluslararası yasak / Banned", "Bilim kurgu / Sci-fi"]},
    {"id": "poll_23", "question": "🧠 Beyin-bilgisayar arayüzleri (Neuralink vb.) insan hafızasını hackleyebilir mi?\n🇬🇧 Can brain-computer interfaces hack human memory?", "options": ["Evet, çok tehlikeli / Very dangerous", "Sadece tedavi amaçlı / Medical only", "Asla hacklenemez / Unhackable"]},
    {"id": "poll_24", "question": "🏙️ Akıllı şehirler bireyleri 7/24 denetleyen birer toplama kampına mı dönüşüyor?\n🇬🇧 Are smart cities turning into concentration camps monitoring individuals 24/7?", "options": ["Kesinlikle evet / Absolutely yes", "Güvenlik için gerekli / Needed for safety", "Abartı / Exaggeration"]},
    {"id": "poll_25", "question": "🌊 Küresel iklim krizini durdurmak için 'Geoengineering' (iklim mühendisliği) risk almaya değer mi?\n🇬🇧 Is geoengineering worth the risk to stop global climate crisis?", "options": ["Değer, başka çare yok / Worth it", "Felakete yol açar / Leads to disaster", "Doğasına bırakılmalı / Leave it natural"]},
    {"id": "poll_26", "question": "☄️ Dünya'ya yaklaşan büyük bir asteroiti yok edebilecek nükleer savunma sistemimiz hazır mı?\n🇬🇧 Are we ready with nuclear defense systems to destroy an incoming asteroid?", "options": ["Evet, hazırız / Yes, ready", "Kısmen hazır / Partially", "Hiçbir hazırlık yok / No preparation"]},
    {"id": "poll_27", "question": "💰 Kripto paralar ve merkeziyetsiz finans gelecekte devletlerin parasal monopolünü bitirecek mi?\n🇬🇧 Will decentralized finance end state monetary monopolies in the future?", "options": ["Kesinlikle bitirecek / Will end", "Devletler yasaklar / States will ban", "Sistemle bütünleşir / Will integrate"]},
    {"id": "poll_28", "question": "🔬 CERN'deki parçacık hızlandırıcıları kazara bir mini karadelik oluşturabilir mi?\n🇬🇧 Can particle accelerators at CERN accidentally create a mini black hole?", "options": ["Teorik olarak evet / Theoretically yes", "İmkansız / Impossible", "Oluştu ama kapandı / Created and closed"]},
    {"id": "poll_29", "question": "🥽 Tamamen sanal gerçeklik (Metaverse) içinde yaşamak fiziksel dünyadan kaçış mı yoksa evrim mi?\n🇬🇧 Is living in virtual reality an escape from the physical world or evolution?", "options": ["Büyük bir kaçış / Big escape", "Geleceğin evrimi / Future evolution", "Zaman kaybı / Waste of time"]},
    {"id": "poll_30", "question": "🕳️ Karadeliklerin içi başka bir evrene açılan geçitler (Einstein-Rosen köprüsü) olabilir mi?\n🇬🇧 Can the inside of black holes be bridges to another universe?", "options": ["Oldukça muhtemel / Highly probable", "Sadece matematiksel model / Mathematical model", "Bilmiyoruz / Unknown"]},
    {"id": "poll_31", "question": "👽 Hükümetlerin UFO dosyalarını resmi olarak açıklaması toplumsal paniğe yol açtı mı?\n🇬🇧 Did official government UFO disclosures cause social panic?", "options": ["Hiçbir panik olmadı / No panic", "İnsanlar umursamadı / People didn't care", "Zaten herkes biliyordu / Everyone knew"]},
    {"id": "poll_32", "question": "🧪 Yapay zeka tarafından keşfedilen yeni malzemeler insanlığı on yıllar öne taşıyabilir mi?\n🇬🇧 Can new materials discovered by AI advance humanity decades ahead?", "options": ["Kesinlikle taşıyacak / Definitely will", "Abartılıyor / Exaggerated", "Riskler barındırır / Contains risks"]},
    {"id": "poll_33", "question": "🌐 Küresel uyduların kesilmesi durumunda insanlık kaç saat içinde kaosa sürüklenir?\n🇬🇧 Within how many hours would humanity plunge into chaos if global satellites failed?", "options": ["Birkaç saat içinde / Within hours", "Birkaç gün içinde / Within days", "Dayanıklıktayız / We are resilient"]},
    {"id": "poll_34", "question": "🏭 Otonom fabrikalar ve robot işçiler küresel işsizlik krizine yol açacak mı?\n🇬🇧 Will autonomous factories and robot workers lead to a global unemployment crisis?", "options": ["Evet, kaçınılmaz / Inevitable", "Yeni iş kolları doğar / New jobs emerge", "Devlet maaş bağlar / Universal basic income"]},
    {"id": "poll_35", "question": "🧬 CRISPR ve gen düzenleme teknolojileri ile ölümsüzlük sınırı aşılabilir mi?\n🇬🇧 Can the limit of immortality be crossed with CRISPR and gene editing?", "options": ["Ömrü uzatır ama ölümsüzlük olmaz / Extends life", "Kesinlikle aşılır / Will be crossed", "Etik olarak engellenir / Ethically blocked"]},
    {"id": "poll_36", "question": "📡 Uzaydan gelen gizemli hızlı radyo patlamaları (FRB) akıllı bir medeniyetin sinyali olabilir mi?\n🇬🇧 Could mysterious fast radio bursts from space be signals from an intelligent civilization?", "options": ["Oldukça yüksek ihtimal / High probability", "Doğal kozmik olay / Natural cosmic event", "Kara delik çarpışması / Black hole collision"]},
    {"id": "poll_37", "question": "🕶️ Artırılmış gerçeklik (AR) kontakt lensler akıllı telefonların yerini tamamen alacak mı?\n🇬🇧 Will augmented reality (AR) contact lenses completely replace smartphones?", "options": ["Kesinlikle alacak / Definitely will", "Sağlığa zararlı olur / Harmful to health", "Gerek kalmaz / Unnecessary"]},
    {"id": "poll_38", "question": "🔋 Füzyon enerjisi (Yapay Güneş) 2030'lara kadar ticari olarak hayatımıza girebilir mi?\n🇬🇧 Can fusion energy enter our lives commercially by the 2030s?", "options": ["Evet, yakındayız / Yes, close", "2050'yi bulur / Takes until 2050", "Asla başaramayız / Never achieve"]},
    {"id": "poll_39", "question": "🗺️ Yeraltı tünel ağları ve Hyperloop sistemleri gelecekte şehirler arası ana ulaşım mı olacak?\n🇬🇧 Will underground tunnel networks and Hyperloop systems be main transit?", "options": ["Evet, çok hızlı / Yes, very fast", "Çok maliyetli / Too expensive", "Gerek yok / Unnecessary"]},
    {"id": "poll_40", "question": "🦠 Laboratuvar sızıntısı teorileri gelecekteki biyolojik krizlerin önlenmesinde ders oldu mu?\n🇬🇧 Have lab leak theories served as a lesson to prevent future biological crises?", "options": ["Hiçbir ders alınmadı / No lessons learned", "Şeffaflık arttı / Transparency increased", "Daha da gizleniyor / Hidden more"]},
    {"id": "poll_41", "question": "🤖 Ev tipi insansı robotlar her haneye girdiğinde insan psikolojisi nasıl etkilenir?\n🇬🇧 How will human psychology be affected when humanoid robots enter every home?", "options": ["Yalnızlık azalır / Loneliness decreases", "İnsanlar yabancılaşır / Alienation", "Bağımlılık yaratır / Addiction"]},
    {"id": "poll_42", "question": "🔍 Deepfake teknolojisi ve yapay sesler hukuki sistemleri tamamen çökertir mi?\n🇬🇧 Will deepfake tech and AI voices completely collapse legal systems?", "options": ["Evet, kanıt kalmaz / No evidence left", "Yeni güvenlik sistemleri çıkar / New systems emerge", "Kısmen etkiler / Partially"]},
    {"id": "poll_43", "question": "🪐 Mars'ta kurulacak ilk insan kolonisi Dünya'dan bağımsız bir cumhuriyet ilan edebilir mi?\n🇬🇧 Can the first human colony on Mars declare independence from Earth?", "options": ["Kesinlikle eder / Definitely", "Dünya'ya bağımlı kalır / Remains dependent", "Kaos çıkar / Chaos ensues"]},
    {"id": "poll_44", "question": "🧠 İnsan bilinci tamamen bir diske (silikon çipe) aktarılabilir mi?\n🇬🇧 Can human consciousness be fully transferred to a silicon chip?", "options": ["Evet, dijital ölümsüzlük / Digital immortality", "Bilinç aktarılamaz / Consciousness cannot be copied", "Sadece kopyası olur / Just a copy"]},
    {"id": "poll_45", "question": "⚖️ Küresel yapay zeka regülasyonları inovasyonu yavaşlatır mı yoksa insanlığı korur mu?\n🇬🇧 Do global AI regulations slow down innovation or protect humanity?", "options": ["İnovasyonu öldürür / Kills innovation", "İnsanlığı korur / Protects humanity", "Dengeyi bulur / Finds balance"]},
    {"id": "poll_46", "question": "🌊 Denizaltı veri merkezleri ve okyanus tabanlı bulut sunucuları geleceğin standardı mı?\n🇬🇧 Are subsea data centers and ocean-based cloud servers the future standard?", "options": ["Evet, soğutma avantajı var / Great cooling", "Bakımı çok zor / Too hard to maintain", "Gereksiz lüks / Unnecessary luxury"]},
    {"id": "poll_47", "question": "⚡ Atmosferik elektriği hasat edip evleri aydınlatmak Tesla gibi büyük ölçekte mümkün mü?\n🇬🇧 Is harvesting atmospheric electricity possible on a large scale like Tesla envisioned?", "options": ["Bilimsel olarak evet / Scientifically yes", "Fizik kurallarına aykırı / Against physics", "Deneniyor / Being tested"]},
    {"id": "poll_48", "question": "🌀 Çoklu evren (Multiverse) teorisi matematiksel bir fantezi mi yoksa test edilebilir gerçeklik mi?\n🇬🇧 Is the Multiverse theory a mathematical fantasy or testable reality?", "options": ["Test edilebilir / Testable", "Saf fantezi / Pure fantasy", "Kuantum gerçekliği / Quantum reality"]},
    {"id": "poll_49", "question": "🛰️ Yörünge çöplüğü (Kessler Sendromu) uzay çalışmalarını tamamen kilitleyebilir mi?\n🇬🇧 Can orbital debris (Kessler Syndrome) completely lock down space exploration?", "options": ["Evet, büyük tehlike / Huge danger", "Temizleme teknolojileri çıkar / Cleanup tech", "Düşük risk / Low risk"]},
    {"id": "poll_50", "question": "🔮 Singularity (Tekillik) noktasına ulaşıldığında insanlık ile yapay zeka birleşecek mi?\n🇬🇧 Will humanity and AI merge when the Singularity point is reached?", "options": ["Syborg evrim kaçınılmaz / Cyborg evolution", "Yapay zeka bizi ezer / AI crushes us", "Yollar ayrılır / Paths separate"]}
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
    """Dünyadan anlık haberleri tarayan, mükerrerliği önleyen ve diske kaydeden fonksiyon"""
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
                available_polls = [p for p in POLL_POOL if p['id'] not in sent_poll_ids]
                if not available_polls:
                    sent_poll_ids.clear()
                    available_polls = POLL_POOL
                    
                poll = random.choice(available_polls)
                sent_poll_ids.append(poll['id'])
                
                send_telegram_poll(poll["question"], poll["options"])
                print("📊 Kanal anketi fırlatıldı.")
                
        except Exception as ex:
            print(f"Döngü hatası: {ex}")
            
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
