import os
import logging
from fastapi import FastAPI, Request, HTTPException
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot import types
import asyncio
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot Configuration
BOT_TOKEN = os.getenv("BOT_TOKEN", "7835189612:AAF6tluzNvRoWdR5FQaOTADO7mdVJWcie1U")
CHANNEL_ID = -1002589515039  # @Anofes
REQUIRED_CHATS = ["@Anofes", "@Mwtlan", "@KhamahdalysRoom"]

# Initialize bot
try:
    bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
    logger.info("Bot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize bot: {e}")
    bot = None

# Initialize FastAPI app
app = FastAPI(title="Menfes Telegram Bot", version="1.0")

# In-memory state storage
state: Dict[int, Any] = {}

def join_buttons():
    """Create inline keyboard for channel joining"""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢 Join @Anofes", url="https://t.me/Anofes"))
    kb.add(InlineKeyboardButton("👥 Join Mwtlan", url="https://t.me/Mwtlan"))
    kb.add(InlineKeyboardButton("📺 Join KhamahdalysRoom", url="https://t.me/KhamahdalysRoom"))
    kb.add(InlineKeyboardButton("✅ Saya Sudah Join", callback_data="check_join"))
    return kb

@app.get("/")
async def health_check():
    """Health check endpoint"""
    return {"status": "Menfes API Aktif", "bot_status": "active" if bot else "inactive"}

@app.post("/")
async def handle_webhook(request: Request):
    """Handle Telegram webhook updates"""
    if not bot:
        raise HTTPException(status_code=500, detail="Bot not initialized")
    
    try:
        json_data = await request.json()
        logger.info(f"Received webhook: {json_data}")
        
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
        
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing webhook: {str(e)}")

@app.get("/bot/info")
async def bot_info():
    """Get bot information"""
    if not bot:
        return {"error": "Bot not initialized"}
    
    try:
        bot_info = bot.get_me()
        return {
            "bot_id": bot_info.id,
            "bot_username": bot_info.username,
            "bot_first_name": bot_info.first_name,
            "status": "active"
        }
    except Exception as e:
        logger.error(f"Error getting bot info: {e}")
        return {"error": str(e)}

# Bot Command Handlers
@bot.message_handler(commands=['start'])
def handle_start(message):
    """Handle /start command"""
    try:
        user_id = message.chat.id
        user_name = message.from_user.first_name or "User"
        
        logger.info(f"User {user_id} ({user_name}) started the bot")
        
        # Set user state
        state[user_id] = "choose_lang"
        
        # Create language selection keyboard
        lang_kb = InlineKeyboardMarkup()
        lang_kb.add(
            InlineKeyboardButton("🇮🇩 Indonesia", callback_data="lang_id"),
            InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
        )
        
        welcome_text = f"👋 Halo {user_name}!\n\n🌐 Pilih bahasa / Choose your language:"
        
        bot.send_message(
            user_id, 
            welcome_text, 
            reply_markup=lang_kb
        )
        
    except Exception as e:
        logger.error(f"Error in handle_start: {e}")
        bot.send_message(message.chat.id, "❌ Terjadi kesalahan. Silakan coba lagi.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def handle_language_selection(call):
    """Handle language selection"""
    try:
        user_id = call.message.chat.id
        language = call.data.split("_")[1]  # id or en
        
        logger.info(f"User {user_id} selected language: {language}")
        
        # Update state
        state[user_id] = {"state": "verifying", "language": language}
        
        # Edit message to show verification in progress
        bot.edit_message_text(
            "🔎 Memeriksa keanggotaan kamu...",
            user_id,
            call.message.message_id
        )
        
        # Send join instruction
        join_text = "📢 Gabung dulu ke komunitas ini ya:"
        bot.send_message(user_id, join_text, reply_markup=join_buttons())
        
    except Exception as e:
        logger.error(f"Error in handle_language_selection: {e}")
        bot.send_message(call.message.chat.id, "❌ Terjadi kesalahan. Silakan coba lagi.")

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def handle_join_check(call):
    """Handle join verification"""
    try:
        user_id = call.message.chat.id
        not_joined = []
        
        logger.info(f"Checking membership for user {user_id}")
        
        # Check membership in all required channels
        for chat in REQUIRED_CHATS:
            try:
                member = bot.get_chat_member(chat, user_id)
                if member.status not in ("member", "administrator", "creator"):
                    not_joined.append(chat)
                    logger.info(f"User {user_id} not a member of {chat}")
            except Exception as e:
                logger.warning(f"Error checking membership in {chat}: {e}")
                not_joined.append(chat)
        
        if not_joined:
            # User hasn't joined all channels
            missing_text = f"❗ Kamu belum join semua channel.\n\nYang belum: {', '.join(not_joined)}\n\nGabung dulu ya:"
            bot.send_message(user_id, missing_text, reply_markup=join_buttons())
        else:
            # User has joined all channels
            state[user_id] = "wait_msg"
            success_text = "✅ Verifikasi sukses!\n\n💬 Sekarang kirim pesan anonim kamu:"
            bot.send_message(user_id, success_text)
            
    except Exception as e:
        logger.error(f"Error in handle_join_check: {e}")
        bot.send_message(call.message.chat.id, "❌ Terjadi kesalahan saat verifikasi. Silakan coba lagi.")

@bot.message_handler(func=lambda msg: state.get(msg.chat.id) == "wait_msg")
def handle_message_input(msg):
    """Handle user message input"""
    try:
        user_id = msg.chat.id
        text = msg.text.strip() if msg.text else ""
        
        logger.info(f"User {user_id} sent message: {text[:50]}...")
        
        if not text:
            bot.send_message(user_id, "❗ Pesan tidak boleh kosong. Kirim pesan teks.")
            return
        
        # Store message in state
        state[user_id] = {
            "state": "preview",
            "text": text,
            "original_message_id": msg.message_id
        }
        
        # Create preview
        preview_text = f"🎭 Preview Pesan Anonim:\n\n💬 \"{text}\"\n\n📤 Kirim ke channel @Anofes sekarang?"
        
        # Create confirmation keyboard
        confirm_kb = InlineKeyboardMarkup()
        confirm_kb.add(
            InlineKeyboardButton("✅ Ya, kirim sekarang!", callback_data="send_now"),
            InlineKeyboardButton("✏️ Ubah pesan", callback_data="edit_msg")
        )
        
        bot.send_message(user_id, preview_text, reply_markup=confirm_kb)
        
    except Exception as e:
        logger.error(f"Error in handle_message_input: {e}")
        bot.send_message(msg.chat.id, "❌ Terjadi kesalahan. Silakan coba lagi.")

@bot.callback_query_handler(func=lambda call: call.data == "edit_msg")
def handle_edit_message(call):
    """Handle message editing"""
    try:
        user_id = call.message.chat.id
        state[user_id] = "wait_msg"
        
        bot.send_message(user_id, "✏️ Baik, kirim pesan baru kamu:")
        
    except Exception as e:
        logger.error(f"Error in handle_edit_message: {e}")
        bot.send_message(call.message.chat.id, "❌ Terjadi kesalahan.")

@bot.callback_query_handler(func=lambda call: call.data == "send_now")
def handle_send_message(call):
    """Handle sending message to channel"""
    try:
        user_id = call.message.chat.id
        user_data = state.get(user_id)
        
        if not isinstance(user_data, dict) or not user_data.get("text"):
            bot.send_message(user_id, "❌ Tidak ada pesan untuk dikirim.")
            return
        
        message_text = user_data["text"]
        
        # Format message for channel
        channel_message = f"🎭 Pesan Anonim\n\n💬 \"{message_text}\"\n\n📝 Dikirim melalui @TextMenfesbot"
        
        # Send to channel
        try:
            bot.send_message(CHANNEL_ID, channel_message)
            logger.info(f"Message sent to channel from user {user_id}")
            
            # Reset user state
            state[user_id] = None
            
            # Confirm to user
            success_text = "✅ Pesan berhasil dikirim ke channel @Anofes!\n\n🔄 Kirim /start untuk mengirim pesan lain."
            bot.send_message(user_id, success_text)
            
        except Exception as e:
            logger.error(f"Error sending message to channel: {e}")
            bot.send_message(user_id, "❌ Gagal mengirim pesan ke channel. Silakan coba lagi.")
            
    except Exception as e:
        logger.error(f"Error in handle_send_message: {e}")
        bot.send_message(call.message.chat.id, "❌ Terjadi kesalahan.")

# Error handler
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Handle all other messages"""
    try:
        user_id = message.chat.id
        user_state = state.get(user_id)
        
        if not user_state:
            bot.send_message(user_id, "👋 Halo! Kirim /start untuk memulai.")
        else:
            bot.send_message(user_id, "❓ Perintah tidak dimengerti. Gunakan tombol yang tersedia atau kirim /start.")
            
    except Exception as e:
        logger.error(f"Error in handle_all_messages: {e}")

# Initialize bot info on startup
if bot:
    try:
        bot_info = bot.get_me()
        logger.info(f"Bot @{bot_info.username} is ready!")
    except Exception as e:
        logger.error(f"Error getting bot info: {e}")