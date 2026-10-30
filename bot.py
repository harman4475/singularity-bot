import logging
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------------------------------------------------------
# AYARLAR (Singularity Hub - Çok Dilli İstihbarat Üssü)
# ---------------------------------------------------------
BOT_TOKEN = "9068851091:AAER43Llfdf_mbVJ13Z831PRCad00R4zaLA"
CHAT_ID = "-1004449764057"
POST_INTERVAL_MINUTES = 60  # Saat başı derin arşiv paylaşımı

# ---------------------------------------------------------
# 1. ÇOK DİLLİ DERİN İSTİHBARAT VE SIR DOSYALARI HAVUZU
# ---------------------------------------------------------
INTEL_HUB = [
    {
        "type": "📂 DECLASSIFIED STATE ARCHIVES / DEVLET ARŞİVLERİ",
        "title_tr": "Kamuya Açıklanan Resmi Epstein Belgeleri ve Küresel Elit Ağları",
        "title_en": "Declassified Official Court Documents & Global Elite Networks",
        "title_ar": "وثائق المحكمة الرسمية السرية وشبكات النخب العالمية",
        "title_hi": "डिक्ลาสिफाइड आधिकारिक अदालत के दस्तावेज और वैश्विक कुलीन नेटवर्क",
        "desc_tr": "Mahkeme kararlarıyla kamuoyuna açıklanan resmi yasal belgelerde, küresel elitlerin gizli bağlantıları ve mahkemeye sunulan sansürsüz declassified dosyalardaki sarsıcı detaylar.",
        "desc_en": "Unsealed and declassified official court documents revealing details about the networks of global elites, sourced entirely from public legal archives.",
        "desc_ar": "وثائق قانونية رسمية تم رفع السرية عنها تكشف تفاصيل شبكات النخب العالمية المستمدة من الأرشيف القانوني العام.",
        "desc_hi": "सार्वजनिक कानूनी अभिलेखों से प्राप्त वैश्विक कुलीन नेटवर्क के विवरण का खुलासा करने वाले आधिकारिक अदालत के दस्तावेज.",
        "link": "https://www.documentcloud.org",
        "tag": "StateArchives"
    },
    {
        "type": "☢️ NUCLEAR SECRETS / NÜLEER VE GİZLİ SİLAHLAR",
        "title_tr": "Atom Bombası Tarihinin Bilinmeyen Karanlık Yüzü ve Gizli Projeler",
        "title_en": "The Unknown Dark Side of Nuclear History and Secret Projects",
        "title_ar": "الجانب المظلم المجهول من التاريخ النووي والمشاريع السرية",
        "title_hi": "परमाणु इतिहास का अज्ञात अंधा पक्ष और गुप्त परियोजनाएं",
        "desc_tr": "Soğuk savaş döneminde nükleer silahların geliştirilmesi aşamasında üstü örtbas edilen kazalar, kayıp nükleer başlıklar ve devletlerin gizli silah programları.",
        "desc_en": "Covered-up accidents, lost nuclear warheads, and classified weapons programs during the height of Cold War atomic development.",
        "desc_ar": "حوادث تم التستر عليها، الرؤوس الحربية النووية المفقودة، وبرامج الأسلحة المصنفة سرية خلال ذروة تطوير الذرة في الحرب الباردة.",
        "desc_hi": "शीत युद्ध के परमाणु विकास के दौरान छुपाए गए हादसे, खोए हुए परमाणु हथियार और वर्गीकृत गुप्त हथियार कार्यक्रम.",
        "link": "https://nsarchive.gwu.edu/",
        "tag": "NuclearSecrets"
    },
    {
        "type": "🇨🇳 ASIAN INTELLIGENCE / ÇİN VE KUZEY KORE SIRLARI",
        "title_tr": "Pekin ve Pyongyang'ın Gizli Arşivlerinden Sızan Küresel Hamleler",
        "title_en": "Leaked Global Moves from Beijing and Pyongyang's Secret Archives",
        "title_ar": "تحركات عالمية مسربة من الأرشيف السري لبكين وبيونغ يانغ",
        "title_hi": "बीजिंग और प्योंगयांग के गुप्त अभिलेखों से लीक हुए वैश्विक कदम",
        "desc_tr": "Doğu blokunun en kapalı kutularından sızdırılan, küresel ekonomik ve askeri dengeleri altüst eden stratejik sırlar ve yeraltı projeleri.",
        "desc_en": "Strategic secrets and underground projects leaked from the closed loops of Eastern bloc intelligence, altering global economic and military balances.",
        "desc_ar": "أسرار استراتيجية ومشاريع تحت الأرض مسربة من الحلقات المغلقة لاستخبارات الكتلة الشرقية، مما أدى إلى تغيير التوازنات الاقتصادية والعسكرية.",
        "desc_hi": "पूर्वी ब्लॉक के गुप्त इंटेलिजेंस से लीक हुए रणनीतिक रहस्य जो वैश्विक आर्थिक और सैन्य संतुलन को बदलते हैं.",
        "link": "https://www.wilsoncenter.org/program/cold-war-international-history-project",
        "tag": "AsianIntel"
    },
    {
        "type": "👁️ DEEP WEB REALITIES / DEEP WEB'İN GERÇEK YÜZÜ",
        "title_tr": "Deep Web Aslında Niçin Kuruldu? İstihbarat Amaçlı Gizli Ağlar",
        "title_en": "Why Deep Web Was Actually Created: Intelligence Purpose Networks",
        "title_ar": "لماذا تم إنشاؤه حقاً: شبكات الاستخبارات السرية في الويب العميقة",
        "title_hi": "डीप वेब वास्तव में क्यों बनाया गया था: खुफिया प्रयोजन नेटवर्क",
        "desc_tr": "Popüler kültürün aksine, karanlık ağların asıl kuruluş amacının askeri istihbarat gizliliği, hükümet haberleşmesi ve sansür karşıtı veri transferi olması.",
        "desc_en": "Contrary to popular culture, the true origin of dark networks built for military intelligence secrecy, government communications, and secure data routing.",
        "desc_ar": "خلافاً للثقافة الشعبية، فإن الأصل الحقيقي للشبكات المظلمة تم بناؤه لأغراض سرية الاستخبارات العسكرية والاتصالات الحكومية.",
        "desc_hi": "लोकप्रिय संस्कृति के विपरीत, डार्क नेटवर्क का असली उद्देश्य सैन्य खुफिया गोपनीयता और सरकारी संचार था.",
        "link": "https://en.wikipedia.org/wiki/Deep_web",
        "tag": "DeepWebTruth"
    },
    {
        "type": "🤖 AI FUTURE & US PRESS / YAPAY ZEKA VE AMERİKAN BASINI",
        "title_tr": "ABD Basınından Sızanlar: Yapay Zeka Modellerinin Kontrolden Çıktığı Anlar",
        "title_en": "US Press Reports: When AI Models Crossed Uncharted Ethical Lines",
        "title_ar": "تقارير الصحافة الأمريكية: عندما تجاوزت نماذج الذكاء الاصطناعي الخطوط الأخلاقية",
        "title_hi": "अमेरिकी प्रेस रिपोर्ट: जब एआई मॉडल ने अनकही नैतिक सीमाएं पार कीं",
        "desc_tr": "ABD'nin önde gelen teknoloji yayınlarında ve akademik makalelerinde tartışılan, yapay zeka sistemlerinin insan denetimini aşma girişimleri ve gizli protokolleri.",
        "desc_en": "Discussions from leading US tech publications and academic papers regarding AI neural networks bypassing human oversight protocols.",
        "desc_ar": "مناقشات من منشورات التكنولوجيا الأمريكية الرائدة والأوراق الأكاديمية حول تجاوز شبكات الذكاء الاصطناعي لبروتوكولات الرقابة البشرية.",
        "desc_hi": "मानव निरीक्षण प्रोटोकॉल को दरकिनार करने वाले एआई तंत्र के बारे में अग्रणी अमेरिकी तकनीकी प्रकाशनों की चर्चाएँ.",
        "link": "https://www.technologyreview.com/",
        "tag": "AIMystery"
    },
    {
        "type": "🗺️ GLOBAL INTELLIGENCE / CIA FOIA ARŞİVLERİ",
        "title_tr": "CIA Bilgi Özgürlüğü Yasası (FOIA) Kapsamında Serbest Bırakılan Gizli Dosyalar",
        "title_en": "CIA Freedom of Information Act (FOIA) Declassified Vault",
        "title_ar": "قبو وكالة المخابرات المركزية الأمريكية للوثائق السرية (FOIA)",
        "title_hi": "सीआईए फ्रीडम ऑफ इंफॉर्मेशन एक्ट (FOIA) डिक्लासिफाइड वॉल्ट",
        "desc_tr": "ABD istihbaratının gizliliğini kaldırarak elektronik okuma odasına yüklediği, tarihin akışını değiştiren zihin kontrol ve casusluk projeleri.",
        "desc_en": "The official CIA Freedom of Information Act electronic reading room featuring declassified historical intelligence reports and psychological operations.",
        "desc_ar": "غرفة القراءة الإلكترونية الرسمية لقانون حرية المعلومات التابع لوكالة المخابرات المركزية والتي تضم تقارير استخباراتية تاريخية سرية.",
        "desc_hi": "सीआईए का आधिकारिक इलेक्ट्रॉनिक रीडिंग रूम जिसमें डिक्लासिफाइड ऐतिहासिक खुफिया रिपोर्ट शामिल हैं.",
        "link": "https://www.cia.gov/readingroom/",
        "tag": "StateSecrets"
    }
]

# ---------------------------------------------------------
# 2. GÜNÜN GİZEMLİ FALI HAVUZU (Mükerrer Korumalı)
# ---------------------------------------------------------
FORTUNE_HUB = [
    {
        "title_tr": "🔮 Günün İstihbarat Falı: Bilinmeyen Frekans",
        "title_en": "🔮 Daily Intel Fortune: The Unknown Frequency",
        "desc_tr": "Bugün küresel ağlarda dönen enerjiler, gizli bir anlaşmanın veya uzun süredir aradığın bir sorunun cevabının önüne çıkacağını gösteriyor. Çevrendeki dijital sinyallere dikkat et.",
        "desc_en": "The energies circulating in global networks today indicate that a secret agreement or the answer to a long-sought question will cross your path. Pay attention to digital signals around you."
    },
    {
        "title_tr": "🔮 Günün İstihbarat Falı: Gölgeler ve Strateji",
        "title_en": "🔮 Daily Intel Fortune: Shadows and Strategy",
        "desc_tr": "Kriptik bir dönemdesin. Bugün alacağın ani bir haber, kariyerinde veya planlarında radikal bir rota değişikliğine sebep olabilir. Sezgilerine güven.",
        "desc_en": "You are in a cryptic phase. Sudden news you receive today may cause a radical change of course in your career or plans. Trust your intuition."
    },
    {
        "title_tr": "🔮 Günün İstihbarat Falı: Matrisin Çatlağı",
        "title_en": "🔮 Daily Intel Fortune: The Matrix Crack",
        "desc_tr": "Sistem içindeki rutinleri kırmak için mükemmel bir gün. Bugün karşına çıkacak şifreli bir detay, hayatındaki büyük bir bulmacayı çözmeni sağlayacak.",
        "desc_en": "An excellent day to break routines within the system. An encrypted detail you encounter today will help you solve a major puzzle in your life."
    }
]

# ---------------------------------------------------------
# 3. TARİHTE BUGÜN / GİZLİ OLAYLAR HAVUZU (Mükerrer Korumalı)
# ---------------------------------------------------------
HISTORY_HUB = [
    {
        "title_tr": "📜 Tarihte Bugün: Gizli Projelerin Perde Arkası",
        "desc_tr": "Tarihin bu gününde, hükümetlerin resmi olarak reddettiği ancak yıllar sonra sızdırılan gizli bir teknoloji programı, dünya askeri dengelerini değiştiren testler gerçekleştirdi."
    },
    {
        "title_tr": "📜 Tarihte Bugün: Kayıp Arşivlerin Gün Işığına Çıkışı",
        "desc_tr": "Yıllarca mühürlü kalan uluslararası istihbarat raporları, tarihin bu gününde ilk kez kamuoyuna serbest bırakıldı ve ezber bozan gerçekler gözler önüne serildi."
    },
    {
        "title_tr": "📜 Tarihte Bugün: Yeraltı Tünelleri Sızıntısı",
        "desc_tr": "Tarihin bu gününde, devletlerin onlarca yıldır haritalardan sildiği devasa yeraltı askeri komplekslerinin varlığı ilk kez resmi belgelerle ifşa edildi."
    }
]

# ---------------------------------------------------------
# 4. UZAY, SİBER & YERALTI ALARMI HAVUZU (Mükerrer Korumalı)
# ---------------------------------------------------------
TECH_HUB = [
    {
        "title_tr": "🛰️ Kozmik İstihbarat & Siber Alarm",
        "desc_tr": "Derin uzaydan gelen anormal sinyaller ve küresel ağlarda tespit edilen gizemli siber hareketlilik, teknoloji otoritelerini alarm durumuna geçirdi."
    },
    {
        "title_tr": "👁️ Siber Casusluk ve Offshore Raporu",
        "desc_tr": "Küresel ölçekte faaliyet gösteren gizli bir hacker grubu, offshore hesaplarda dönen trilyonlarca dolarlık karanlık fon ağını sızdırdı."
    },
    {
        "title_tr": "🧠 Zihin Kontrolü ve MK-Ultra Arşivleri",
        "desc_tr": "Devletlerin geçmişte insan davranışı ve algı yönetimi üzerine yürüttüğü gizli zihin kontrol projelerine ait yeni sansürsüz belgeler gün yüzüne çıktı."
    }
]

# Mükerrer (Tekrar) Paylaşımı Tamamen Önleyen Geçmiş Takip Listeleri
sent_intel_history = []
sent_fortune_history = []
sent_history_history = []
sent_tech_history = []

# ---------------------------------------------------------
# GÖREV FONKSİYONLARI (Akıllı Mükerrer Engelleme Mekanizmasıyla)
# ---------------------------------------------------------

async def post_hub_content(context: ContextTypes.DEFAULT_TYPE):
    """Saat başı derin istihbarat arşivi paylaşır (Asla mükerrer olmaz)"""
    global sent_intel_history
    
    if len(sent_intel_history) >= len(INTEL_HUB):
        sent_intel_history = []
        
    available_items = [item for item in INTEL_HUB if item not in sent_intel_history]
    if not available_items:
        available_items = INTEL_HUB
        
    item = random.choice(available_items)
    sent_intel_history.append(item)
    
    caption = (
        f"🌐 <b>SINGULARITY INTEL HUB</b>\n"
        f"🏷️ <code>{item['type']}</code>\n\n"
        f"🇬🇧 <b>{item['title_en']}</b>\n"
        f"🇹🇷 <b>{item['title_tr']}</b>\n"
        f"🇸🇦 <b>{item['title_ar']}</b>\n"
        f"🇮🇳 <b>{item['title_hi']}</b>\n\n"
        f"🇬🇧 <i>{item['desc_en']}</i>\n\n"
        f"🇹🇷 <i>{item['desc_tr']}</i>\n\n"
        f"🇸🇦 <i>{item['desc_ar']}</i>\n\n"
        f"🇮🇳 <i>{item['desc_hi']}</i>\n\n"
        f"📌 #{item['tag']}"
    )
    
    keyboard = [[InlineKeyboardButton("🔗 Arşivi İncele / Source / المصدر / स्रोत", url=item['link'])]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await context.bot.send_message(
            chat_id=CHAT_ID,
            text=caption,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        print("✅ Saat başı istihbarat dosyası başarıyla servis edildi.")
    except Exception as e:
        print(f"❌ Gönderim hatası: {e}")

async def post_daily_fortune(context: ContextTypes.DEFAULT_TYPE):
    """Günde 1 defa günün falını gönderir (Mükerrer içermez)"""
    global sent_fortune_history
    
    if len(sent_fortune_history) >= len(FORTUNE_HUB):
        sent_fortune_history = []
        
    available_items = [item for item in FORTUNE_HUB if item not in sent_fortune_history]
    if not available_items:
        available_items = FORTUNE_HUB
        
    item = random.choice(available_items)
    sent_fortune_history.append(item)
    
    caption = (
        f"🔮 <b>SINGULARITY DAILY FORTUNE / GÜNÜN FALI</b>\n\n"
        f"🇹🇷 <b>{item['title_tr']}</b>\n"
        f"<i>{item['desc_tr']}</i>\n\n"
        f"🇬🇧 <b>{item['title_en']}</b>\n"
        f"<i>{item['desc_en']}</i>\n\n"
        f"👁️ #DailyFortune #SingularityHub"
    )
    try:
        await context.bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="HTML")
        print("🔮 Günün falı servis edildi.")
    except Exception as e:
        print(f"❌ Fal gönderim hatası: {e}")

async def post_daily_poll(context: ContextTypes.DEFAULT_TYPE):
    """Günde 1 defa üyelerin etkileşimi için anket gönderir"""
    polls = [
        ("🧠 SİNGULARİTY ANKETİ: Sizce önümüzdeki 10 yıl içinde yapay zeka insanlığı yönetmeye başlayacak mı?", 
         ["Kesinlikle Başlayacak", "İnsan Kontrolü Elde Tutacak", "Sistem Çökecek / Kaos Olacak", "Bunu Zaten Yapıyorlar"]),
        ("🌐 KÜRESEL MERAK: Sizce dünyayı arkadan yöneten gizli bir konsey veya elit ağ var mı?", 
         ["Kesinlikle Var", "Tamamen Komplo Teorisi", "Sadece Büyük Şirketler Yönetiyor", "Bilmiyorum / Düşünüyorum"]),
        ("🛸 UZAY VE GERÇEKLER: Sizce dünya dışı akıllı yaşam formları hükümetler tarafından gizleniyor mu?", 
         ["Evet, Kesinlikle Saklıyorlar", "Hayır, Öyle Bir Şey Yok", "Zaten Aramızdalar", "Emin değilim"])
    ]
    poll_data = random.choice(polls)
    try:
        await context.bot.send_poll(
            chat_id=CHAT_ID,
            question=poll_data[0],
            options=poll_data[1],
            is_anonymous=False
        )
        print("📊 Günlük anket servis edildi.")
    except Exception as e:
        print(f"❌ Anket gönderim hatası: {e}")

async def post_history_event(context: ContextTypes.DEFAULT_TYPE):
    """Günde 1 defa tarihte bugün gizemli olay paylaşır (Mükerrer içermez)"""
    global sent_history_history
    
    if len(sent_history_history) >= len(HISTORY_HUB):
        sent_history_history = []
        
    available_items = [item for item in HISTORY_HUB if item not in sent_history_history]
    if not available_items:
        available_items = HISTORY_HUB
        
    item = random.choice(available_items)
    sent_history_history.append(item)
    
    caption = (
        f"📜 <b>SINGULARITY CHRONICLES / TARİHTE BUGÜN</b>\n\n"
        f"🇹🇷 <b>{item['title_tr']}</b>\n"
        f"<i>{item['desc_tr']}</i>\n\n"
        f"📌 #History #DarkArchives"
    )
    try:
        await context.bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="HTML")
        print("📜 Tarih olayı servis edildi.")
    except Exception as e:
        print(f"❌ Tarih gönderim hatası: {e}")

async def post_tech_alarm(context: ContextTypes.DEFAULT_TYPE):
    """Günde 1 defa uzay, siber ve yeraltı alarm bülteni paylaşır (Mükerrer içermez)"""
    global sent_tech_history
    
    if len(sent_tech_history) >= len(TECH_HUB):
        sent_tech_history = []
        
    available_items = [item for item in TECH_HUB if item not in sent_tech_history]
    if not available_items:
        available_items = TECH_HUB
        
    item = random.choice(available_items)
    sent_tech_history.append(item)
    
    caption = (
        f"🚨 <b>SINGULARITY TECH & UNDERGROUND ALARM</b>\n\n"
        f"🇹🇷 <b>{item['title_tr']}</b>\n"
        f"<i>{item['desc_tr']}</i>\n\n"
        f"🛰️ #CyberIntel #Underground #SpaceAnomaly"
    )
    try:
        await context.bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="HTML")
        print("🚨 Tech alarm servis edildi.")
    except Exception as e:
        print(f"❌ Tech alarm gönderim hatası: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 <b>Singularity Hub İstihbarat Üssüne Hoş Geldiniz!</b>\n\n"
        "This channel automatically serves global state secrets, nuclear intelligence, "
        "daily fortunes, interactive polls, underground intel, and breaking news in <b>English, Turkish, Arabic, and Hindi</b>.\n\n"
        "<i>Sadece gerçekler, sırlar, anlık flaşlar ve küresel gündem.</i>"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    
    job_queue = app.job_queue
    if job_queue:
        # 1. Başlangıçta hemen test paylaşımı
        job_queue.run_once(post_hub_content, when=3)
        
        # 2. Saat başı derin arşiv paylaşımları (Her 60 dakikada bir)
        job_queue.run_repeating(post_hub_content, interval=POST_INTERVAL_MINUTES * 60, first=60)
        
        # 3. Günde 1 kez Günün Falı (Her 24 saatte bir)
        job_queue.run_repeating(post_daily_fortune, interval=86400, first=300)
        
        # 4. Günde 1 kez İnteraktif Anket (Her 24 saatte bir)
        job_queue.run_repeating(post_daily_poll, interval=86400, first=600)
        
        # 5. Günde 1 kez Tarihte Bugün (Her 24 saatte bir)
        job_queue.run_repeating(post_history_event, interval=86400, first=900)
        
        # 6. Günde 1 kez Uzay & Yeraltı Alarmı (Her 24 saatte bir)
        job_queue.run_repeating(post_tech_alarm, interval=86400, first=1200)
    
    print(f"🚀 Çok dilli Singularity Hub kusursuz ve mükerrer korumalı olarak aktif!")
    app.run_polling()

if __name__ == '__main__':
    main()