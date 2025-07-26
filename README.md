# Menfes Text - Telegram Bot System

## 🎯 Overview
Anonymous message system (Menfes) using Telegram bot with FastAPI webhook for Vercel deployment.

## 🚫 What This System Does NOT Use:
- ❌ React, Next.js, or any frontend framework
- ❌ MongoDB or any external database
- ❌ Media uploads (images, audio, stickers)

## ✅ What This System Uses:
- FastAPI for webhook handling
- pyTelegramBotAPI (telebot) for bot functionality
- In-memory state cache for user sessions
- Vercel-ready deployment configuration

## 📁 Project Structure
```
menfes-text/
├── main.py                    # Main bot implementation for Vercel
├── backend/
│   ├── server.py             # FastAPI + Telegram bot server
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment variables
├── vercel.json               # Vercel deployment configuration
├── requirements.txt          # Root dependencies for Vercel
└── backend_test.py           # Comprehensive backend tests
```

## 🔧 Configuration
- **BOT_TOKEN**: Telegram bot token
- **CHANNEL_ID**: -1002589515039 (@Anofes)
- **REQUIRED_CHATS**: ["@Anofes", "@Mwtlan", "@KhamahdalysRoom"]

## 🌐 Deployment
Deploy to Vercel:
1. Set environment variable: `BOT_TOKEN=your_bot_token`
2. Deploy project
3. Set webhook: `https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://your-vercel-url`

## 📱 Bot Flow
1. User sends `/start`
2. Language selection (🇮🇩/🇬🇧)
3. Channel membership verification
4. Anonymous message composition
5. Message preview and confirmation
6. Message sent to @Anofes channel

## 🔍 Health Check
GET `/` returns: `{"status": "Menfes API Aktif"}`
