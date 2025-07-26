# main.py
import os
from fastapi import FastAPI, Request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🚫 Tanpa React, Tanpa MongoDB, Tanpa Frontend
# ✅ FastAPI + Telebot (pyTelegramBotAPI) Only

BOT_TOKEN = os.getenv("BOT_TOKEN", "7835189612:AAF6tluzNvRoWdR5FQaOTADO7mdVJWcie1U")
CHANNEL_ID = -1002589515039  # @Anofes
REQUIRED_CHATS = ["@Anofes", "@Mwtlan", "@KhamahdalysRoom"]

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
app = FastAPI()

# In-memory state storage
state = {}

def join_buttons():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("📢 Join @Anofes", url="https://t.me/Anofes"))
    kb.add(InlineKeyboardButton("👥 Join Mwtlan", url="https://t.me/Mwtlan"))
    kb.add(InlineKeyboardButton("📺 Join KhamahdalysRoom", url="https://t.me/KhamahdalysRoom"))
    kb.add(InlineKeyboardButton("✅ Saya Sudah Join", callback_data="check_join"))
    return kb

@app.post("/")
async def handle_webhook(request: Request):
    json_data = await request.json()
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])
    return {"ok": True}

@app.get("/")
def health_check():
    return {"status": "Menfes API Aktif"}

@bot.message_handler(commands=["start"])
def on_start(message):
    state[message.chat.id] = "choose_lang"
    lang_kb = InlineKeyboardMarkup()
    lang_kb.add(
        InlineKeyboardButton("🇮🇩 Indonesia", callback_data="lang_id"),
        InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    bot.send_message(message.chat.id, "🌐 Pilih bahasa / Choose your language:", reply_markup=lang_kb)

@bot.callback_query_handler(func=lambda call: call.data.startswith("lang_"))
def on_lang_selected(call):
    user_id = call.message.chat.id
    state[user_id] = "verifying"
    bot.edit_message_text("🔎 Memeriksa keanggotaan kamu...", user_id, call.message.message_id)
    bot.send_message(user_id, "Gabung dulu ke komunitas ini ya:", reply_markup=join_buttons())

@bot.callback_query_handler(func=lambda call: call.data == "check_join")
def on_check_join(call):
    user_id = call.message.chat.id
    not_joined = []
    
    for chat in REQUIRED_CHATS:
        try:
            member = bot.get_chat_member(chat, user_id)
            if member.status not in ("member", "administrator", "creator"):
                not_joined.append(chat)
        except:
            not_joined.append(chat)
    
    if not_joined:
        bot.send_message(user_id, "❗ Kamu belum join semua. Gabung dulu ya:", reply_markup=join_buttons())
    else:
        state[user_id] = "wait_msg"
        bot.send_message(user_id, "✅ Verifikasi sukses. Kirim pesan anonim kamu sekarang.")

@bot.message_handler(func=lambda msg: state.get(msg.chat.id) == "wait_msg")
def on_message_received(msg):
    text = msg.text.strip() if msg.text else ""
    
    if not text:
        bot.send_message(msg.chat.id, "❗ Teks tidak boleh kosong.")
        return
    
    state[msg.chat.id] = {"state": "preview", "text": text}
    
    preview = f"🎭 Pesan Anonim\n💬 \"{text}\"\n\nKirim ke channel sekarang?"
    
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("✅ Ya, kirim sekarang", callback_data="send_now"),
        InlineKeyboardButton("✏️ Ubah Pesan", callback_data="edit_msg")
    )
    
    bot.send_message(msg.chat.id, preview, reply_markup=kb)

@bot.callback_query_handler(func=lambda call: call.data == "edit_msg")
def on_edit(call):
    state[call.message.chat.id] = "wait_msg"
    bot.send_message(call.message.chat.id, "✏️ Kirim ulang pesan kamu.")

@bot.callback_query_handler(func=lambda call: call.data == "send_now")
def on_send(call):
    user_id = call.message.chat.id
    data = state.get(user_id)
    
    if isinstance(data, dict) and data.get("text"):
        bot.send_message(CHANNEL_ID, f"🎭 Pesan Anonim\n💬 \"{data['text']}\"")
        state[user_id] = None
        bot.send_message(user_id, "✅ Pesan sudah dikirim ke channel!")
    else:
        bot.send_message(user_id, "❌ Tidak ada pesan untuk dikirim.")
