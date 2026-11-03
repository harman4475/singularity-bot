import os
import time
import json
import random
import threading
from datetime import datetime
import feedparser
import requests
from flask import Flask, request
from deep_translator import GoogleTranslator

app = Flask(__name__)

# ================= CONFIGURATION =================
TELEGRAM_BOT_TOKEN = "9068851091:AAEkDBT-28x1L1CErISM3qxEAJRRGgAZV98"
TELEGRAM_CHAT_ID = "-1004449764057"
HISTORY_FILE = "sent_news_history.json"
POLL_INTERVAL = 60  # Döngü hızı (Saniye)

LIVE_RSS_FEEDS = [
    "https://www.aa.com.tr/tr/rss/default?cat=guncel",
    "https://www.trthaber.com/sondakika.rss",
    "https://www.ntv.com.tr/son-dakika.rss",
    "https://www.haberturk.com/rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.space.com/home/feed/site.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.dw.com/rdf/rss-en-top"
]

# ================= GENİŞLETİLMİŞ KÜRESEL ANKET HAVUZU =================
GLOBAL_POLLS_POOL = [
    {
        "tr": "🤖 Yapay Zeka (AGI) önümüzdeki 10 yılda senin mesleğini tamamen ortadan kaldırabilir mi?",
        "en": "🤖 Could Artificial Intelligence (AGI) completely eliminate your profession in the next 10 years?",
        "options": ["Evet, kaçış yok / Yes, inevitable", "Hayır, insan şart / No, humans needed"]
    },
    {
        "tr": "🚀 Mars'a tek yönlü bir koloni yolculuğu teklif edilse, dünyayı arkada bırakıp gider miydin?",
        "en": "🚀 If offered a one-way colony trip to Mars, would you leave Earth behind and go?",
        "options": ["Hemen giderim! / I'd go right now!", "Asla, Dünya güzel / Never, Earth is home"]
    },
    {
        "tr": "🧠 Hafızanı bir buluta yedekleyip ölümsüzleşme şansın olsa, kabul eder miydin?",
        "en": "🧠 If you had the chance to back up your memory to a cloud and achieve immortality, would you accept?",
        "options": ["Kesinlikle kabul ederim / Definitely accept", "Doğal döngü bozulmamalı / Nature shouldn't be altered"]
    },
    {
        "tr": "💊 Günde sadece 3 saat uyumanı sağlayan ama ömrünü kısaltmayan bir hap olsa içer miydin?",
        "en": "💊 If there was a pill allowing you to sleep only 3 hours a day without shortening your life, would you take it?",
        "options": ["Günde 21 saat bana kalır! / 21 free hours for me!", "Risk almam, uykum kutsal / No risks, sleep is sacred"]
    },
    {
        "tr": "🕶️ Tamamen dijital, gerçekçi bir sanal gerçeklik dünyasında ömrünün sonuna kadar yaşamak ister miydin?",
        "en": "🕶️ Would you want to live out the rest of your life in a completely digital, hyper-realistic virtual reality world?",
        "options": ["Hemen bağlanırım / Plug me in right now", "Gerçek acı bile tatlıdır / Real pain over fake bliss"]
    },
    {
        "tr": "💰 Eline ömür boyu çalışmayacağın kadar para geçse ilk ne yapardın?",
        "en": "💰 If you suddenly got enough money to never work again, what would you do first?",
        "options": ["Dünyayı gezerim / Travel the world", "Yeni projeler kurarım / Build new projects"]
    },
    {
        "tr": "⚖️ Yapay zeka kritik bir suç işlediğinde, ceza kod yazana mı yoksa yapay zekanın kendisine mi kesilmeli?",
        "en": "⚖️ When an AI commits a critical crime, should the punishment go to the developer or the AI itself?",
        "options": ["Kod yazana / To the developer", "Yapay zekaya / To the AI"]
    },
    {
        "tr": "🌐 İnsanlık için en büyük varoluşsal tehdit hangisidir?",
        "en": "🌐 What is the greatest existential threat to humanity?",
        "options": ["Kontrolsüz Yapay Zeka / Rogue AI", "İklim Krizi / Climate Crisis"]
    },
    {
        "tr": "🚗 Sürücüsüz otonom araçlara tamamen güvenip arka koltukta uyuyabilir misin?",
        "en": "🚗 Would you completely trust fully autonomous self-driving cars and sleep in the back seat?",
        "options": ["Gözümü kırpmadan uyurum / Sleep soundly", "Asla direksiyonsuz olmaz / Never without a steering wheel"]
    },
    {
        "tr": "🧬 Genetik olarak tasarlanmış (süper zeki veya atletik) bebekler yasal hale gelmeli mi?",
        "en": "🧬 Should genetically engineered (super-smart or athletic) designer babies become legal?",
        "options": ["Evet, evrimsel sıçrama / Yes, evolutionary leap", "Kesinlikle yasaklanmalı / Strictly prohibited"]
    },
    {
