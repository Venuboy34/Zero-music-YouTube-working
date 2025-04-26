import os
import time
import logging
import requests
from threading import Thread
from flask import Flask, request

import telebot
from yt_dlp import YoutubeDL

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Token and App URL
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_DEFAULT_BOT_TOKEN")
APP_URL = os.getenv("APP_URL", "https://your-koyeb-app-name.koyeb.app")  # Set your Koyeb App URL here

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# Global Variables
download_count = 0
bot_start_time = time.time()

# Utils
def sanitize_filename(filename):
    illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    return filename

def keep_alive():
    """Optional Keep Alive Pings (not needed on Koyeb usually)"""
    while True:
        logger.info("Keep-alive ping")
        time.sleep(600)

# Handlers
@bot.message_handler(commands=['start'])
def handle_start(message):
    name = message.from_user.first_name
    welcome_image = "https://envs.sh/C_W.jpg"
    caption = (
        f"✨🎶 *Welcome, {name}!* 🎶✨\n\n"
        "I am your *Music Bot*! Send me the name of a song or artist.\n\n"
        "💬 *Examples:*\n"
        "`Shape of You - Ed Sheeran`\n"
        "`Senorita - Shawn Mendes`\n\n"
        "📜 *Commands:*\n"
        "• /start - Restart Bot\n"
        "• /help - See Commands\n"
        "• /stats - Bot Stats\n"
        "• /test - YouTube Connection Check\n\n"
        "🚀 *Created with love by* [Zero Creations](https://t.me/zerocreations)"
    )
    bot.send_photo(
        message.chat.id,
        welcome_image,
        caption=caption,
        parse_mode="Markdown",
        disable_web_page_preview=True
    )

@bot.message_handler(commands=['help'])
def handle_help(message):
    help_text = (
        "*Available Commands:*\n\n"
        "• Type song or artist name to search\n"
        "• /start - Welcome Message\n"
        "• /help - Help Commands\n"
        "• /stats - Bot Statistics\n"
        "• /test - Check YouTube Connection\n\n"
        "*Examples:*\n"
        "`Imagine Dragons Believer`\n"
        "`Senorita Shawn Mendes`"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['test'])
def handle_test(message):
    try:
        with YoutubeDL({'quiet': True, 'extract_flat': True, 'skip_download': True}) as ydl:
            search = ydl.extract_info("ytsearch1:test", download=False)
        if search and search.get('entries'):
            bot.send_message(message.chat.id, "✅ YouTube connection successful!", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⚠️ YouTube connected but no results!", parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Test error: {e}")
        bot.send_message(message.chat.id, f"❌ YouTube connection failed.\n\nError: `{e}`", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def handle_stats(message):
    uptime_seconds = time.time() - bot_start_time
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    stats = (
        "📊 *Bot Stats:*\n\n"
        f"🎵 Downloads: *{download_count}*\n"
        f"⏱ Uptime: *{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s*\n"
        f"👤 Created by: @zerocreations"
    )
    bot.send_message(message.chat.id, stats, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_music_request(message):
    global download_count

    query = message.text.strip()
    user_name = message.from_user.first_name
    chat_id = message.chat.id

    bot.send_chat_action(chat_id, 'typing')
    status = bot.reply_to(message, f"🔎 Searching for: *{query}*", parse_mode="Markdown")

    try:
        os.makedirs("downloads", exist_ok=True)
        file_base = f"downloads/{int(time.time())}"

        with YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
            result = ydl.extract_info(f"ytsearch1:{query}", download=False)
        if not result or not result.get('entries'):
            bot.edit_message_text(
                "⚠️ No results found. Try another search.",
                chat_id, status.message_id
            )
            return

        bot.edit_message_text("🎶 Found! Downloading audio...", chat_id, status.message_id, parse_mode="Markdown")
        bot.send_chat_action(chat_id, 'upload_audio')

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"{file_base}.%(ext)s",
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)['entries'][0]

        title = sanitize_filename(info.get('title', 'Unknown'))
        artist = info.get('uploader', 'Unknown')
        duration = info.get('duration', 0)
        url = info.get('webpage_url')
        views = info.get('view_count', 0)
        thumb_url = info.get('thumbnail')

        mp3_file = f"{file_base}.mp3"
        if os.path.getsize(mp3_file) > 50 * 1024 * 1024:
            bot.edit_message_text(
                "⚠️ Audio file too large (>50MB). Try a shorter song.",
                chat_id, status.message_id
            )
            os.remove(mp3_file)
            return

        thumb_file = None
        if thumb_url:
            thumb_file = f"{file_base}_thumb.jpg"
            with open(thumb_file, 'wb') as f:
                f.write(requests.get(thumb_url).content)

        min, sec = divmod(duration, 60)
        duration_str = f"{int(min)}:{sec:02d}"

        with open(mp3_file, 'rb') as audio:
            thumb_param = {}
            if thumb_file and os.path.exists(thumb_file):
                with open(thumb_file, 'rb') as thumb:
                    thumb_param['thumb'] = thumb
                    bot.send_audio(
                        chat_id,
                        audio,
                        title=title,
                        performer=artist,
                        caption=(
                            f"🎵 *{title}*\n"
                            f"👤 _{artist}_\n"
                            f"⏱ {duration_str}\n"
                            f"👁 {views:,} views\n\n"
                            f"[YouTube Link]({url})\n\n"
                            f"Enjoy, {user_name}! 🎧\n\n"
                            f"Powered by @zerocreations"
                        ),
                        parse_mode="Markdown",
                        **thumb_param
                    )
            else:
                bot.send_audio(
                    chat_id,
                    audio,
                    title=title,
                    performer=artist,
                    caption=(
                        f"🎵 *{title}*\n"
                        f"👤 _{artist}_\n"
                        f"⏱ {duration_str}\n"
                        f"👁 {views:,} views\n\n"
                        f"[YouTube Link]({url})\n\n"
                        f"Enjoy, {user_name}! 🎧\n\n"
                        f"Powered by @zerocreations"
                    ),
                    parse_mode="Markdown"
                )

        bot.delete_message(chat_id, status.message_id)
        download_count += 1

        os.remove(mp3_file)
        if thumb_file and os.path.exists(thumb_file):
            os.remove(thumb_file)

    except Exception as e:
        logger.error(f"Music Search Error: {e}")
        bot.edit_message_text(
            "⚠️ *Oops! Something went wrong.*\nPlease try searching for a different song name.",
            chat_id, status.message_id,
            parse_mode="Markdown"
        )

# Webhook Routes
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return "Bot is running!"

@app.route(f"/{BOT_TOKEN}", methods=['POST'])
def webhook():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return 'ok', 200

# Main
def main():
    Thread(target=keep_alive, daemon=True).start()

    webhook_url = f"{APP_URL}/{BOT_TOKEN}"
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=webhook_url)
    logger.info(f"Webhook set to {webhook_url}")

    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

if __name__ == "__main__":
    main()
