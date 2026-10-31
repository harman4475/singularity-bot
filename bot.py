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
# 3. TARİHTE BUGÜN / GİZLİ OLAYLAR HAVUZU (Çok Dilli
