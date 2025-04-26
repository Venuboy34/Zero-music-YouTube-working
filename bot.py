import telebot
from yt_dlp import YoutubeDL
import os
import requests
import logging
import time
from threading import Thread

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7607542715:AAEFjEb3RQ38ztOE4DkqMxGQQL5uCN4WZPw")
bot = telebot.TeleBot(BOT_TOKEN)

def sanitize_filename(filename):
    """Remove illegal characters from filenames"""
    illegal_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in illegal_chars:
        filename = filename.replace(char, '_')
    return filename

# Statistics tracking
download_count = 0

# Keep-alive function for preventing service from sleeping
def keep_alive():
    while True:
        logger.info("Keep-alive ping")
        time.sleep(600)  # Ping every 10 minutes

@bot.message_handler(commands=['start'])
def welcome(message):
    name = message.from_user.first_name
    welcome_image_url = "https://envs.sh/C_W.jpg"
    
    bot.send_photo(
        message.chat.id,
        welcome_image_url,
        caption=f"🎧 Hello {name}!\n\nSend me a *music name* and I'll find it on YouTube, extract the audio, and send it back to you as MP3!\n\n🔍 Just type something like:\n`Believer by Imagine Dragons`\n\n/help - Show more commands\n/test - Check YouTube connectivity",
        parse_mode="Markdown"
    )
    
@bot.message_handler(commands=['test'])
def test_connection(message):
    """Test bot connectivity to YouTube"""
    try:
        # Test connection to YouTube
        test_query = "test song"
        with YoutubeDL({'quiet': True, 'extract_flat': True, 'skip_download': True}) as ydl:
            search_results = ydl.extract_info(f"ytsearch1:{test_query}", download=False)
            
            if search_results and len(search_results.get('entries', [])) > 0:
                bot.send_message(
                    message.chat.id,
                    "✅ Bot is working correctly and can connect to YouTube.",
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(
                    message.chat.id,
                    "⚠️ Bot can connect to YouTube but search results are empty.",
                    parse_mode="Markdown"
                )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Connection test failed: {str(e)}",
            parse_mode="Markdown"
        )

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "*Commands and Usage:*\n\n"
        "• Simply type a song name or artist to search\n"
        "• /start - Welcome message\n"
        "• /help - Show this help message\n"
        "• /stats - Show bot statistics\n"
        "• /test - Check YouTube connectivity\n\n"
        "*Examples:*\n"
        "`Bohemian Rhapsody`\n"
        "`Dua Lipa New Rules`\n"
        "`Blinding Lights The Weeknd`"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats(message):
    uptime = time.time() - bot_start_time
    days, remainder = divmod(uptime, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    stats_text = (
        "📊 *Bot Statistics*\n\n"
        f"🎵 Downloads: *{download_count}*\n"
        f"⏱ Uptime: *{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s*\n"
        f"👥 Created by: @zerocreations"
    )
    bot.send_message(message.chat.id, stats_text, parse_mode="Markdown")

@bot.message_handler(func=lambda msg: True)
def music_search(message):
    global download_count
    search_query = message.text
    name = message.from_user.first_name
    
    # Send "typing..." action
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Send search message
    status_message = bot.reply_to(message, f"🔎 Searching for: *{search_query}*...", parse_mode="Markdown")

    # Directory for downloads
    os.makedirs("downloads", exist_ok=True)
    file_path = f"downloads/{int(time.time())}"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'outtmpl': f'{file_path}.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
    }

    try:
        # First check if search returns results
        with YoutubeDL({'quiet': True, 'extract_flat': True}) as ydl:
            search_results = ydl.extract_info(f"ytsearch1:{search_query}", download=False)
            
            if not search_results or len(search_results.get('entries', [])) == 0:
                bot.edit_message_text(
                    "⚠️ No results found. Please try a different search query.",
                    message.chat.id,
                    status_message.message_id
                )
                return
        
        # Update status message
        bot.edit_message_text(
            f"🔎 Found! Downloading audio...", 
            message.chat.id, 
            status_message.message_id,
            parse_mode="Markdown"
        )
        
        # Send "upload_audio" action
        bot.send_chat_action(message.chat.id, 'upload_audio')
        
        with YoutubeDL(ydl_
            
            # Use sanitized filename
            title_safe = sanitize_filename(title)
            filename = f"{file_path}.mp3"
            
            # If file is too large for Telegram (>50MB)
            file_size = os.path.getsize(filename) / (1024 * 1024)  # Size in MB
            if file_size > 50:
                bot.edit_message_text(
                    f"⚠️ The audio file is too large ({file_size:.1f}MB). Telegram allows max 50MB.\n\nTry a shorter song.",
                    message.chat.id,
                    status_message.message_id
                )
                os.remove(filename)
                return

        # Handle thumbnail download only if available
        thumb_file = None
        if thumbnail_url:
            thumb_file = f"{file_path}_thumb.jpg"
            r = requests.get(thumbnail_url)
            with open(thumb_file, 'wb') as f:
                f.write(r.content)

        # Update status message with more detailed info
        bot.edit_message_text(
            f"🎵 *{title}*\n👤 By: _{artist}_\n\n📤 Converting and uploading to Telegram...\nPlease wait, this may take a few moments.", 
            message.chat.id, 
            status_message.message_id,
            parse_mode="Markdown"
        )
        
        # Add a small delay to ensure user sees the status
        time.sleep(1)

        # Format duration
        minutes, seconds = divmod(duration, 60)
        duration_str = f"{int(minutes)}:{int(seconds):02d}"

        # Send the audio with or without thumbnail
        with open(filename, 'rb') as audio:
            if thumb_file and os.path.exists(thumb_file):
                with open(thumb_file, 'rb') as thumb:
                    bot.send_audio(
                        message.chat.id, 
                        audio, 
                        title=title, 
                        performer=artist,
                        thumb=thumb,
                        caption=f"🎵 *{title}*\n👤 By: _{artist}_\n⏱ Duration: {duration_str}\n👁 Views: {view_count:,}\n\n[YouTube Link]({webpage_url})\n\nEnjoy, {name}! 🎧\n\nPowered by @zerocreations",
                        parse_mode="Markdown"
                    )
                os.remove(thumb_file)
            else:
                bot.send_audio(
                    message.chat.id, 
                    audio, 
                    title=title, 
                    performer=artist,
                    caption=f"🎵 *{title}*\n👤 By: _{artist}_\n⏱ Duration: {duration_str}\n👁 Views: {view_count:,}\n\n[YouTube Link]({webpage_url})\n\nEnjoy, {name}! 🎧\n\nPowered by @zerocreations",
                    parse_mode="Markdown"
                )

        # Delete the status message after successful send
        bot.delete_message(message.chat.id, status_message.message_id)
        
        # Increment download counter
        download_count += 1
        
        # Clean up
        os.remove(filename)

    except Exception as e:
        logger.error(f"Error: {e}")
        bot.edit_message_text(
            "⚠️ Error: Couldn't find or download the music. Please try another search query.",
            message.chat.id,
            status_message.message_id
        )
        # Clean up any created files
        for ext in ['.mp3', '_thumb.jpg']:
            if os.path.exists(f"{file_path}{ext}"):
                os.remove(f"{file_path}{ext}")

def main():
    global bot_start_time
    bot_start_time = time.time()
    
    # Start keep-alive thread
    keep_alive_thread = Thread(target=keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()
    
    logger.info("Bot started!")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)

if __name__ == "__main__":
    main()
