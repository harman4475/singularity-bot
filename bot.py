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

# 🏛️ KÜRESEL TEKNOLOJİ, YAPAY ZEKA, SİBER GÜVENLİK, TELEGRAM VE FELSEFE ANSİKLOPEDİSİ (ULTRA-CLASSIFIED HUB)
ULTRA_CLASSIFIED
