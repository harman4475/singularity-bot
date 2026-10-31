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
    return "Singularity Hub Global Multi-Language Bot is active!", 200

def run_web():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ---------------------------------------------------------
# AYARLAR 
# ---------------------------------------------------------
BOT_TOKEN = "9068851091:AAFFpGSBNjJa3MlhtzeRiA3iKZ8aJ5ETWxE"
CHAT_ID = "-1004449764057"
POST_INTERVAL_MINUTES = 60  # Her 1 saatte bir evrensel post atar

# ---------------------------------------------------------
# KÜRESEL ÇOK DİLLİ İSTİHBARAT VE KEŞİF HAVUZU
# ---------------------------------------------------------
GLOBAL_INTEL_HUB = [
    {
        "type": "📂 DECLASSIFIED STATE ARCHIVES / ARCHIVES D'ÉTAT",
        "title_en": "Declassified Official Court Documents & Global Elite Networks",
        "title_tr": "Kamuya Açıklanan Resmi Epstein Belgeleri ve Küresel Elit Ağları",
        "title_es": "Documentos Oficiales Desclasificados y Redes de Élites Globales",
        "title_fr": "Documents Officiels Déclassifiés et Réseaux d'Élites Mondiales",
        "title_ar": "وثائق المحكمة الرسمية السرية وشبكات النخب العالمية",
        "title_ru": "Рассекреченные официальные судебные документы и сети глобальной элиты",
        "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?q=80&w=1000&auto=format&fit=crop",
        "link": "https://www.documentcloud.org",
        "tag": "StateArchives"
    },
    {
        "type": "🚀 COSMIC DISCOVERY / DÉCOUVERTE COSMIQUE",
        "title_en": "Deep Space Anomalies Captured by James Webb Space Telescope",
        "title_tr": "James Webb Teleskobu'ndan Gelen Derin Uzay Anormallikleri",
        "title_es": "Anomalías del Espacio Profundo Capturadas por el Telescopio James Webb",
        "title_fr": "Anomalies de l'Espace Profond Capturées par le Télescope James Webb",
        "title_ar": "تشوهات الفضاء العميقة التي التقطها تلسكوب جيمس ويب",
        "title_ru": "Аномалии глубокого космоса, зафиксированные телескопом Джеймса Уэбба",
        "image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=1000&auto=format&fit=crop",
        "link": "https://webbtelescope.org",
        "tag": "CosmicHub"
    },
    {
        "type": "💻 CYBER INTELLIGENCE / CYBER RENSEIGNEMENT",
        "title_en": "Mysterious Code Blocks Detected in Global Financial Networks",
        "title_tr": "Küresel Finans Ağlarında Tespit Edilen Gizemli Kod Blokları",
        "title_es": "Bloques de Código Misteriosos Detectados en Redes Financieras Globales",
        "title_fr": "Blocs de Code Mystérieux Détectés dans les Réseaux Financiers Mondiaux",
        "title_ar": "كتل تعليمات برمجية غامضة تم اكتشافها في الشبكات المالية العالمية",
        "title_ru": "Таинственные блоки кода, обнаруженные в глобальных финансовых сетях",
        "image": "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=1000&auto=format&fit=crop",
        "link": "https://github.com",
        "tag": "CyberAlert"
    }
]

async def send_global_post(context: ContextTypes.DEFAULT_TYPE):
    item = random.choice(GLOBAL_INTEL_HUB)
    caption = (
        f"🌐 <b>SINGULARITY HUB: GLOBAL INTEL</b>\n"
        f"🏷️ <code>{item['type']}</code>\n\n"
        f"🇬🇧 <b>{item['title_en']}</b>\n"
        f"🇹🇷 <b>{item['title_tr']}</b>\n"
        f"🇪🇸 <b>{item['title_es']}</b>\n"
        f"🇫🇷 <b>{item['title_fr']}</b>\n"
        f"🇷🇺 <b>{item['title_ru']}</b>\n"
        f"🇸🇦 <b>{item['title_ar']}</b>\n\n"
        f"📌 #{item['tag']} #GlobalIntelligence #SingularityHub"
    )
    keyboard = [[InlineKeyboardButton("🔗 Kaynağı İncele / Source / Fuente", url=item['link'])]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await context.bot.send_photo(
            chat_id=CHAT_ID,
            photo=item['image'],
            caption=caption,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        print("✅ Küresel çok dilli post başarıyla kanala fırlatıldı!")
    except Exception as e:
        print(f"❌ Gönderim hatası: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🤖 <b>Singularity Hub Global Bot aktif!</b>\n"
        "Tüm evrensel dillerde istihbarat akışı devrede.", 
        parse_mode="HTML"
    )

async def post_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_global_post(context)
    await update.message.reply_text("🚀 Küresel çok dilli istihbarat postu kanala çakıldı usta!")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("post", post_command))
    
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_repeating(lambda ctx: send_global_post(ctx), interval=POST_INTERVAL_MINUTES * 60, first=10)
    
    t = threading.Thread(target=run_web)
    t.daemon = True
    t.start()
    
    print(f"🚀 Global Multi-Language Hub aktif!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
