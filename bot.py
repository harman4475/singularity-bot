import logging
import random
import os
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
# RENDER İÇİN MİNİ WEB SUNUCUSU (Keep-Alive & Health Check)
# ---------------------------------------------------------
web_app = Flask('')

@web_app.route('/')
def home():
    return "Singularity Hub Bot is active and running!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

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
        print("✅ İstihbarat başarıyla kanala gönderildi!")
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
        # Bot ayağa kalktıktan 5 saniye sonra ilk postu atar, sonra her 60 dakikada bir tekrarlar
        job_queue.run_once(post_hub_content, when=5)
        job_queue.run_repeating(post_hub_content, interval=POST_INTERVAL_MINUTES * 60, first=60)
    
    # Flask sunucusunu arka planda başlatıyoruz
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
    
    print(f"🚀 Singularity Hub aktif!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
