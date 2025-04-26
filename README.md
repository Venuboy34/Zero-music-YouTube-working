# Telegram Music Bot (@zerocreations)

A Telegram bot that downloads YouTube music and sends it as MP3 files.

## Features

- Search and download music from YouTube
- Convert videos to MP3 format
- Display song details (title, artist, duration, views)
- Include thumbnail images
- Track download statistics
- Optimized for Koyeb deployment

## Deployment Instructions

### Prerequisites

1. A Telegram Bot Token (from @BotFather)
2. A GitHub repository
3. A Koyeb account (free tier available)

### Setup

1. Clone this repository
2. Replace the BOT_TOKEN in koyeb.yaml with your own token if needed
3. Push to your GitHub repository

### Deploy to Koyeb

**Method 1: Using Koyeb Dashboard**

1. Go to [Koyeb](https://app.koyeb.com/)
2. Create a new application
3. Select "GitHub" as the deployment method
4. Connect your GitHub account and select the repository
5. Use the following settings:
   - Name: telegram-music-bot
   - Builder: Dockerfile
   - Ports: 8080
   - Resources: 512MB RAM, 0.25 CPU (Free tier)
   - Environment Variables: BOT_TOKEN=your_bot_token
6. Deploy

**Method 2: Using Koyeb CLI**

1. Install Koyeb CLI: `curl -fsSL https://raw.githubusercontent.com/koyeb/koyeb-cli/master/install.sh | sh`
2. Login: `koyeb login`
3. Deploy: `koyeb app init`

## Files in This Repository

- `bot.py` - Main bot code
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `koyeb.yaml` - Koyeb deployment configuration

## Bot Commands

- `/start` - Welcome message
- `/help` - Show help information
- `/stats` - Show bot statistics

To use the bot, simply send a message with the name of the song you want to download.

## Maintenance

The bot includes a keep-alive function to prevent it from being suspended on Koyeb's free tier.

## Notes

- Telegram has a 50MB file size limit for bots
- The bot will automatically clean up downloaded files after sending

## Created by @zerocreations
