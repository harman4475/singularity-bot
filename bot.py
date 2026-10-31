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
# İSTİHBARAT HAVUZU
# ---------------------------------------------------------
INTEL_HUB = [
    {
        "type": "📂 DECLASSIFIED STATE ARCHIVES / DEVLET ARŞİVLERİ",
        "title_tr": "Kamuya Açıklanan Resmi Epstein Belgeleri ve Küresel Elit Ağları",
        "title_en": "Declassified Official Court Documents & Global Elite Networks",
        "link": "https://www.documentcloud.org",
        "tag": "StateArchives"
    },
    {
        "type": "☢️ NUCLEAR SECRETS / NÜLEER VE GİZLİ SİLAHLAR",
        "title_tr": "Atom Bombası Tarihinin Bilinmeyen Karanlık Yüzü ve Gizli Projeler",
        "title_en": "The Unknown Dark Side of Nuclear History and Secret Projects",
        "link": "https://nsarchive.gwu.edu/",
        "tag": "NuclearSecrets"
    }
]

async def send_intel_post(context: ContextTypes.DEFAULT_TYPE, chat_id=CHAT_ID):
    item = random.choice(INTEL_HUB)
    caption = (
        f"🌐 <b>SINGULARITY INTEL HUB</b>\n"
        f"🏷️ <code>{item['type']}</code>\n\n"
        f"🇬🇧 <b>{item['title_en']}</b>\n"
        f"🇹🇷 <b>{item['title_tr']}</b>\n\n"
        f"📌 #{item['tag']}"
    )
    keyboard = [[InlineKeyboardButton("🔗 Arşivi İncele / Source", url=item['link'])]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    try:
        await context.bot.send_message(chat_id=chat_id, text=caption, parse_mode="HTML", reply_markup=reply_markup)
        print("✅ İstihbarat başarıyla kanala gönderildi!")
    except Exception as e:
        print(f"❌ Gönderim hatası: {e}")

async def auto_post_job(context: ContextTypes.DEFAULT_TYPE):
    await send_intel_post(context, CHAT_ID)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "🤖 <b>Singularity Hub İstihbarat Üssüne Hoş Geldiniz!</b>\n\n"
        "Bot aktif ve komutları dinliyor."
    )
    await update.message.reply_text(welcome_text, parse_mode="HTML")

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Bu komutu yazdığın an doğrudan kanala test postu atar
    await send_intel_post(context, CHAT_ID)
    await update.message.reply_text("🚀 İstihbarat manuel olarak kanala fırlatıldı usta!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("post", post_command)) # Yeni manuel tetikleyici komut
    
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(auto_post_job, interval=POST_INTERVAL_MINUTES * 60, first=10)
    
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
    
    print(f"🚀 Singularity Hub aktif!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
