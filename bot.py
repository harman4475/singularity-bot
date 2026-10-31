import logging
import random
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# Loglama ayarları
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ---------------------------------------------------------
# RENDER İÇİN MİNİ WEB SUNUCUSU (Kapanmayı Önleyen Sihirli Dokunuş)
# ---------------------------------------------------------
web_app = Flask('')

@web_app.route('/')
def home():
    return "Singularity Hub Bot is active and running!"

def run_web():
    web_app.run(host='0.0.0.0', port=10000)

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
# 2. GÜNÜN GİZEMLİ FALI HAVUZU (Çok Dilli)
# ---------------------------------------------------------
FORTUNE_HUB = [
    {
        "title_tr": "🔮 Günün İstihbarat Falı: Bilinmeyen Frekans",
        "title_en": "🔮 Daily Intel Fortune: The Unknown Frequency",
        "title_ar": "🔮 فبركة الاستخبارات اليومية: التردد المجهول",
        "title_hi": "🔮 दैनिक खुफिया भाग्य: अज्ञात आवृत्ति",
        "desc_tr": "Bugün küresel ağlarda dönen enerjiler, gizli bir anlaşmanın veya uzun süredir aradığın bir sorunun cevabının önüne çıkacağını gösteriyor. Çevrendeki dijital sinyallere dikkat et.",
        "desc_en": "The energies circulating in global networks today indicate that a secret agreement or the answer to a long-sought question will cross your path. Pay attention to digital signals around you.",
        "desc_ar": "تشير الطاقات المتداولة في الشبكات العالمية اليوم إلى أن اتفاقاً سرياً أو إجابة على سؤال طال البحث عنه ستعترض طريقك.",
        "desc_hi": "आज वैश्विक नेटवर्क में घूम रही ऊर्जाएं यह संकेत देती हैं कि एक गुप्त समझौता या लंबे समय से तलाशे जा रहे प्रश्न का उत्तर आपके सामने आएगा।"
    },
    {
        "title_tr": "🔮 Günün İstihbarat Falı: Gölgeler ve Strateji",
        "title_en": "🔮 Daily Intel Fortune: Shadows and Strategy",
        "title_ar": "🔮 فبركة الاستخبارات اليومية: الظلال والاستراتيجية",
        "title_hi": "🔮 दैनिक खुफिया भाग्य: छाया और रणनीति",
        "desc_tr": "Kriptik bir dönemdesin. Bugün alacağın ani bir haber, kariyerinde veya planlarında radikal bir rota değişikliğine sebep olabilir. Sezgilerine güven.",
        "desc_en": "You are in a cryptic phase. Sudden news you receive today may cause a radical change of course in your career or plans. Trust your intuition.",
        "desc_ar": "أنت في مرحلة معقدة. قد تتسبب الأخبار المفاجئة التي تتلقاها اليوم في تغيير جذري في المسار في حياتك المهنية أو خططك.",
        "desc_hi": "आप एक गुप्त चरण में हैं। आज आपको मिलने वाली अचानक की खबर आपके करियर या योजनाओं में बदलाव ला सकती है."
    },
    {
        "title_tr": "🔮 Günün İstihbarat Falı: Matrisin Çatlağı",
        "title_en": "🔮 Daily Intel Fortune: The Matrix Crack",
        "title_ar": "🔮 فبركة الاستخبارات اليومية: صدع الماتريكس",
        "title_hi": "🔮 दैनिक खुफिया भाग्य: मैट्रिक्स क्रैक",
        "desc_tr": "Sistem içindeki rutinleri kırmak için mükemmel bir gün. Bugün karşına çıkacak şifreli bir detay, hayatındaki büyük bir bulmacayı çözmeni sağlayacak.",
        "desc_en": "An excellent day to break routines within the system. An encrypted detail you encounter today will help you solve a major puzzle in your life.",
        "desc_ar": "يوم ممتاز لكسر الروتين داخل النظام. تفصيل مشفر ستواجهه اليوم سيساعدك على حل لغز كبير.",
        "desc_hi": "सिस्टम के भीतर रूटीन को तोड़ने का एक शानदार दिन। आज आपके सामने आने वाला एक एन्क्रिप्टेड विवरण एक बड़े पहेली को सुलझाने में मदद करेगा।"
    }
]

# ---------------------------------------------------------
# 3. TARİHTE BUGÜN / GİZLİ OLAYLAR HAVUZU (Çok Dilli)
# ---------------------------------------------------------
HISTORY_HUB = [
    {
        "title_tr": "Tarihte Bugün: Gizli Projelerin Perde Arkası",
        "title_en": "Today in History: Behind the Scenes of Secret Projects",
        "title_ar": "تاريخ اليوم: كواليس المشاريع السرية",
        "title_hi": "इतिहास में आज: गुप्त परियोजनाओं के पीछे की कहानी",
        "desc_tr": "Tarihin bu gününde, hükümetlerin resmi olarak reddettiği ancak yıllar sonra sızdırılan gizli bir teknoloji programı, dünya askeri dengelerini değiştiren testler gerçekleştirdi.",
        "desc_en": "On this day in history, a classified tech program officially denied by governments but leaked years later conducted tests altering global military balances.",
        "desc_ar": "في مثل هذا اليوم من التاريخ، أجرى برنامج تقني مصنف سراً اختبارات غيرت التوازنات العسكرية العالمية.",
        "desc_hi": "इतिहास में आज के दिन, सरकारों द्वारा आधिकारिक रूप से नकारे गए लेकिन बाद में लीक हुए गुप्त तकनीकी कार्यक्रम ने वैश्विक सैन्य संतुलन को बदला."
    },
    {
        "title_tr": "Tarihte Bugün: Kayıp Arşivlerin Gün Işığına Çıkışı",
        "title_en": "Today in History: The Emergence of Lost Archives",
        "title_ar": "تاريخ اليوم: ظهور الأرشيف المفقود",
        "title_hi": "इतिहास में आज: खोए हुए अभिलेखों का प्रकाश में आना",
        "desc_tr": "Yıllarca mühürlü kalan uluslararası istihbarat raporları, tarihin bu gününde ilk kez kamuoyuna serbest bırakıldı ve ezber bozan gerçekler gözler önüne serildi.",
        "desc_en": "International intelligence reports sealed for years were declassified to the public for the first time on this day in history.",
        "desc_ar": "تم رفع السرية عن تقارير الاستخبارات الدولية المكتومة لسنوات للجمهور لأول مرة في مثل هذا اليوم.",
        "desc_hi": "वर्षों तक सील की गई अंतर्राष्ट्रीय खुफिया रिपोर्टों को इतिहास में आज के दिन पहली बार जनता के लिए डिक्लासिफाइड किया गया था."
    },
    {
        "title_tr": "Tarihte Bugün: Yeraltı Tünelleri Sızıntısı",
        "title_en": "Today in History: Underground Tunnels Leak",
        "title_ar": "تاريخ اليوم: تسريب الأنفاق تحت الأرض",
        "title_hi": "इतिहास में आज: भूमिगत सुरंगों का रिसाव",
        "desc_tr": "Tarihin bu gününde, devletlerin onlarca yıldır haritalardan sildiği devasa yeraltı askeri komplekslerinin varlığı ilk kez resmi belgelerle ifşa edildi.",
        "desc_en": "On this day, the existence of massive underground military complexes erased from maps for decades was officially exposed.",
        "desc_ar": "في هذا اليوم، تم كشف وجود مجمعات عسكرية ضخمة تحت الأرض مسحوبة من الخرائط لعقود.",
        "desc_hi": "आज के दिन, दशकों से नक्शे से मिटाए गए विशाल भूमिगत सैन्य परिसरों के अस्तित्व का आधिकारिक तौर पर खुलासा हुआ।"
    }
]

# ---------------------------------------------------------
# 4. UZAY, SİBER & YERALTI ALARMI HAVUZU (Çok Dilli)
# ---------------------------------------------------------
TECH_HUB = [
    {
        "title_tr": "Kozmik İstihbarat & Siber Alarm",
        "title_en": "Cosmic Intelligence & Cyber Alert",
        "title_ar": "الاستخبارات الكونية والإنذار السيبراني",
        "title_hi": "कॉस्मिक इंटेलिजेंस और साइबर अलर्ट",
        "desc_tr": "Derin uzaydan gelen anormal sinyaller ve küresel ağlarda tespit edilen gizemli siber hareketlilik, teknoloji otoritelerini alarm durumuna geçirdi.",
        "desc_en": "Abnormal signals from deep space and mysterious cyber activity detected in global networks put tech authorities on high alert.",
        "desc_ar": "الإشارات غير الطبيعية من الفضاء العميق والنشاط السيبراني الغامض وضعت سلطات التكنولوجيا في حالة تأهب قصوى.",
        "desc_hi": "गहरे अंतरिक्ष से असामान्य संकेत और वैश्विक नेटवर्क में पाई गई रहस्यमयी साइबर गतिविधि ने तकनीकी अधिकारियों को हाई अलर्ट पर कर दिया है।"
    },
    {
        "title_tr": "Siber Casusluk ve Offshore Raporu",
        "title_en": "Cyber Espionage and Offshore Report",
        "title_ar": "التجسس السيبراني وتقرير الأوفشور",
        "title_hi": "साइबर जासूसी और अपतटीय रिपोर्ट",
        "desc_tr": "Küresel ölçekte faaliyet gösteren gizli bir hacker grubu, offshore hesaplarda dönen trilyonlarca dolarlık karanlık fon ağını sızdırdı.",
        "desc_en": "A covert hacker group operating globally leaked a dark fund network of trillions of dollars circulating in offshore accounts.",
        "desc_ar": "قامت مجموعة تسلل سرية تعمل عالمياً بتسريب شبكة أموال مظلمة تبلغ قيمتها تريليونات الدولارات.",
        "desc_hi": "वैश्विक स्तर पर काम कर रहे एक गुप्त हैकर समूह ने अपतटीय खातों में घूम रहे खरबों डॉलर के काले धन के नेटवर्क को लीक किया।"
    },
    {
        "title_tr": "Zihin Kontrolü ve MK-Ultra Arşivleri",
        "title_en": "Mind Control and MK-Ultra Archives",
        "title_ar": "أرشيف التحكم بالعقل و MK-Ultra",
        "title_hi": "माइंड कंट्रोल और एमके-अльтра अभिलेख",
        "desc_tr": "Devletlerin geçmişte insan davranışı ve algı yönetimi üzerine yürüttüğü gizli zihin kontrol projelerine ait yeni sansürsüz belgeler gün yüzüne çıktı.",
        "desc_en": "New uncensored documents regarding secret mind control projects conducted by states on human behavior and perception management have emerged.",
        "desc_ar": "ظهرت وثائق جديدة غير خاضعة للرقابة تتعلق بمشاريع سرية للسيطرة على العقول نفذتها الدول.",
        "desc_hi": "मानव व्यवहार और धारणा प्रबंधन पर राज्यों द्वारा चलाए गए गुप्तMind Control प्रोजेक्ट्स के नए अनसेंसर्ड दस्तावेज सामने आए हैं।"
    }
]

# Geçmiş Takip Listeleri
sent_intel_history = []
sent_fortune_history = []
sent_history_history = []
sent_tech_history = []

async def post_hub_content(context: ContextTypes.DEFAULT_TYPE):
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
        await context.bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="HTML", reply_markup=reply_markup)
    except Exception as e:
        print(f"❌ Gönderim hatası: {e}")

async def post_daily_fortune(context: ContextTypes.DEFAULT_TYPE):
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
        f"🇹🇷 <b>{item['title_tr']}</b>\n<i>{item['desc_tr']}</i>\n\n"
        f"🇬🇧 <b>{item['title_en']}</b>\n<i>{item['desc_en']}</i>\n\n"
        f"🇸🇦 <b>{item['title_ar']}</b>\n<i>{item['desc_ar']}</i>\n\n"
        f"🇮🇳 <b>{item['title_hi']}</b>\n<i>{item['desc_hi']}</i>\n\n"
        f"👁️ #DailyFortune #SingularityHub"
    )
    try:
        await context.bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="HTML")
    except Exception as e:
        print(f"❌ Fal gönderim hatası: {e}")

async def post_daily_poll(context: ContextTypes.DEFAULT_TYPE):
    polls = [
        ("🧠 SİNGULARİTY ANKETİ / GLOBAL POLL:\nSizce önümüzdeki 10 yıl içinde yapay zeka insanlığı yönetmeye başlayacak mı?\nWill AI start ruling humanity in the next 10 years?", ["Kesinlikle / Absolutely", "İnsan Kontrolü / Human Control", "Kaos Olacak / Chaos", "Zaten Yapıyor / Already Does"]),
        ("🌐 KÜRESEL MERAK / GLOBAL CURIOSITY:\nSizce dünyayı arkadan yöneten gizli bir konsey veya elit ağ var mı?\nIs there a secret council or elite network ruling the world?", ["Kesinlikle Var / Definitely Yes", "Komplo / Conspiracy", "Şirketler / Corporations", "Bilmiyorum / Don't Know"]),
        ("🛸 UZAY VE GERÇEKLER / SPACE & FACTS:\nSizce dünya dışı akıllı yaşam formları hükümetler tarafından gizleniyor mı?\nAre extraterrestrial life forms being hidden by governments?", ["Evet, Saklıyorlar / Yes", "Hayır, Yok / No", "Zaten Aramızdalar / Among Us", "Emin değilim / Not Sure"])
    ]
    poll_data = random.choice(polls)
    try:
        await context.bot.send_poll(chat_id=CHAT_ID, question=poll_data[0], options=poll_data[1], is_anonymous=False)
    except Exception as e:
        print(f"❌ Anket gönderim hatası: {e}")

async def post_history_event(context: ContextTypes.DEFAULT_TYPE):
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
        f"🇬🇧 <b>{item['title_en']}</b>\n<i>{item['desc_en']}</i>\n\n"
        f"🇹🇷 <b>{item['title_tr']}</b>\n<i>{item['desc_tr']}</i>\n\n"
        f"🇸🇦 <b>{item['title_ar']}</b>\n<i>{item['desc_ar']}</i>\n\n"
        f"🇮🇳 <b>{item['title_hi']}</b>\n<i>{item['desc_hi']}</i>\n\n"
        f"📌 #History #DarkArchives"
    )
    try:
        await context.bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="HTML")
    except Exception as e:
        print(f"❌ Tarih gönderim hatası: {e}")

async def post_tech_alarm(context: ContextTypes.DEFAULT_TYPE):
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
        f"🇬🇧 <b>{item['title_en']}</b>\n<i>{item['desc_en']}</i>\n\n"
        f"🇹🇷 <b>{item['title_tr']}</b>\n<i>{item['desc_tr']}</i>\n\n"
        f"🇸🇦 <b>{item['title_ar']}</b>\n<i>{item['desc_ar']}</i>\n\n"
        f"🇮🇳 <b>{item['title_hi']}</b>\n<i>{item['desc_hi']}</i>\n\n"
        f"🛰️ #CyberIntel #Underground #SpaceAnomaly"
    )
    try:
        await context.bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="HTML")
    except Exception as e:
        print(f"❌ Tech alarm gönderim hatası: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 <b>Singularity Hub İstihbarat Üssüne Hoş Geldiniz!</b>\n\n"
        "This channel automatically serves global state secrets, nuclear intelligence, "
        "daily fortunes, interactive polls, underground intel, and breaking news in <b>English, Turkish, Arabic, and Hindi</b>.\n\n"
        "<i>Sadece gerçekler, sırlar, anlık flaşlar ve küresel gündem. / Only facts, secrets, and global agenda.</i>"
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")

def main():
    # Web sunucusunu arka planda (ayrı bir kolda) başlatıyoruz
    t = threading.Thread(target=run_web)
    t.start()
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_once(post_hub_content, when=3)
        job_queue.run_repeating(post_hub_content, interval=POST_INTERVAL_MINUTES * 60, first=60)
        job_queue.run_repeating(post_daily_fortune, interval=86400, first=300)
        job_queue.run_repeating(post_daily_poll, interval=86400, first=600)
        job_queue.run_repeating(post_history_event, interval=86400, first=900)
        job_queue.run_repeating(post_tech_alarm, interval=86400, first=1200)
    
    print(f"🚀 Tamamen küresel ve çok dilli Singularity Hub aktif!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
