import logging
import random
import os
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
BOT_TOKEN = "9068851091:AAFFpGSBNjJa3MlhtzeRiA3iKZ8aJ5ETWxE"
CHAT_ID = "-1004449764057"
POST_INTERVAL_MINUTES = 60

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
    }
]

FORTUNE_HUB = [
    {
        "title_tr": "🔮 Günün İstihbarat Falı: Bilinmeyen Frekans",
        "title_en": "🔮 Daily Intel Fortune: The Unknown Frequency",
        "title_ar": "🔮 فبركة الاستخبارات اليومية: التردد المجهول",
        "title_hi": "🔮 दैनिक खुफिया भाग्य: अज्ञात आवृत्ति",
        "desc_tr": "Bugün küresel ağlarda dönen enerjiler, gizli bir anlaşmanın veya uzun süredir aradığın bir sorunun cevabının önüne çıkacağını gösteriyor.",
        "desc_en": "The energies circulating in global networks today indicate that a secret agreement or the answer to a long-sought question will cross your path.",
        "desc_ar": "تشير الطاقات المتداولة في الشبكات العالمية اليوم إلى أن اتفاقاً سرياً أو إجابة على سؤال طال البحث عنه ستعترض طريقك.",
        "desc_hi": "आज वैश्विक नेटवर्क में घूम रही ऊर्जाएं यह संकेत देती हैं कि एक गुप्त समझौता आपके सामने आएगा."
    }
]

HISTORY_HUB = [
    {
        "title_tr": "Tarihte Bugün: Gizli Projelerin Perde Arkası",
        "title_en": "Today in History: Behind the Scenes of Secret Projects",
        "title_ar": "تاريخ اليوم: كواليس المشاريع السرية",
        "title_hi": "इतिहास में आज: गुप्त परियोजनाओं के पीछे की कहानी",
        "desc_tr": "Tarihin bu gününde, hükümetlerin resmi olarak reddettiği ancak yıllar sonra sızdırılan gizli bir teknoloji programı testler gerçekleştirdi.",
        "desc_en": "On this day in history, a classified tech program officially denied by governments but leaked years later conducted tests.",
        "desc_ar": "في مثل هذا اليوم من التاريخ، أجرى برنامج تقني مصنف سراً اختبارات غيرت التوازنات العسكرية العالمية.",
        "desc_hi": "इतिहास में आज के दिन, सरकारों द्वारा आधिकारिक रूप से नकारे गए गुप्त तकनीकी कार्यक्रम ने परीक्षण किए।"
    }
]

TECH_HUB = [
    {
        "title_tr": "Kozmik İstihbarat & Siber Alarm",
        "title_en": "Cosmic Intelligence & Cyber Alert",
        "title_ar": "الاستخبارات الكونية والإنذار السيبراني",
        "title_hi": "कॉस्मिक इंटेलिजेंस और साइबर अलर्ट",
        "desc_tr": "Derin uzaydan gelen anormal sinyaller ve küresel ağlarda tespit edilen gizemli siber hareketlilik alarm durumuna geçirdi.",
        "desc_en": "Abnormal signals from deep space and mysterious cyber activity detected in global networks put tech authorities on high alert.",
        "desc_ar": "الإشارات غير الطبيعية من الفضاء العميق والنشاط السيبراني الغامض وضعت سلطات التكنولوجيا في حالة تأهب.",
        "desc_hi": "गहरे अंतरिक्ष से असामान्य संकेत और वैश्विक नेटवर्क में पाई गई रहस्यमयी साइबर गतिविधि ने अलर्ट किया।"
    }
]

sent_intel_history = []

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
        f"🇹🇷 <b>{item['title_tr']}</b>\n\n"
        f"🇬🇧 <i>{item['desc_en']}</i>\n\n"
        f"🇹🇷 <i>{item['desc_tr']}</i>\n\n"
        f"📌 #{item['tag']}"
    )
    keyboard = [[InlineKeyboardButton("🔗 Arşivi İncele / Source", url=item['link'])]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await context.bot.send_message(chat_id=CHAT_ID, text=caption, parse_mode="HTML", reply_markup=reply_markup)
    except Exception as e:
        print(f"❌ Gönderim hatası: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 <b>Singularity Hub İstihbarat Üssüne Hoş Geldiniz!</b>\n\n"
        "This channel automatically serves global state secrets and intelligence updates."
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_once(post_hub_content, when=3)
        job_queue.run_repeating(post_hub_content, interval=POST_INTERVAL_MINUTES * 60, first=60)
    
    print(f"🚀 Singularity Hub aktif!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
