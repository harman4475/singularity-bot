async def check_live_news_job(context: ContextTypes.DEFAULT_TYPE):
    """Her 30 saniyede bir çalışıp RSS beslemelerini kontrol eder."""
    try:
        for feed_url in LIVE_RSS_FEEDS:
            req = urllib.request.Request(feed_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                xml_data = response.read()
                root = ET.fromstring(xml_data)
                channel = root.find('channel')
                if channel is not None:
                    item = channel.find('item')
                    if item is not None:
                        title_el = item.find('title')
                        link_el = item.find('link')
                        guid_el = item.find('guid')
                        
                        title = title_el.text if title_el is not None else "Son Dakika İstihbarat"
                        link = link_el.text if link_el is not None else "https://t.me"
                        news_id = guid_el.text if guid_el is not None else title
                        
                        if news_id not in sent_news_ids:
                            sent_news_ids.add(news_id)
                            if len(sent_news_ids) > 100:
                                sent_news_ids.pop()
                                
                            caption = (
                                "⚡ <b>SINGULARITY ULTRA-CLASSIFIED INTEL</b>\n"
                                "🏷️ <code>REAL-TIME FEED ALERT</code>\n\n"
                                f"🚨 <b>{title}</b>\n\n"
                                "🇬🇧 <i>Unfiltered global intelligence feed</i>\n"
                                "🇹🇷 <i>Filtrelenmemiş küresel istihbarat akışı</i>\n"
                                "🇩🇪 <i>Ungefilterter globaler Feed</i>\n"
                                "🇪🇸 <i>Flujo de inteligencia sin filtrar</i>\n"
                                "🇮🇹 <i>Feed di intelligence non filtrato</i>\n"
                                "🇮🇳 <i>फिल्टर न किया गया वैश्विक फ़ीड</i>\n\n"
                                "📌 #BreakingNews #SecretSatellites #SingularityHub"
                            )
                            keyboard = [[InlineKeyboardButton("🔗 Kaynak / Source / Quelle", url=link)]]
                            
                            await context.bot.send_message(
                                chat_id=CHAT_ID,
                                text=caption,
                                parse_mode="HTML",
                                reply_markup=InlineKeyboardMarkup(keyboard)
                            )
                            print(f"⚡ Gizli akış haberi fırlatıldı: {title}")
                            return
    except Exception as e:
        print(f"⚠️ Haber tarama hatası: {e}")
