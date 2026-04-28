import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# 🚨 Render Environment Variables se uthayega
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
ADMIN_ID = os.environ.get('ADMIN_ID') 

bot = telebot.TeleBot(TELEGRAM_TOKEN)

app = Flask('')
@app.route('/')
def home(): return "Direct Support Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    btns = [
        types.InlineKeyboardButton("💰 Deposit Issue", callback_data='deposit'),
        types.InlineKeyboardButton("💸 Withdrawal Info", callback_data='withdraw'),
        types.InlineKeyboardButton("🔑 Room ID & Pass", callback_data='roomid'),
        types.InlineKeyboardButton("📋 Match Rules", callback_data='rules'),
        types.InlineKeyboardButton("🤝 Refer & Earn", callback_data='refer'),
        types.InlineKeyboardButton("👨‍💻 Talk to Admin", callback_data='chat_admin')
    ]
    markup.add(*btns)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 *Namaste!*\n\nMain Esports Arena ka official helper hoon. Aap mujhse direct baat karne ke liye yahan message *Type* kar sakte hain.", reply_markup=main_menu(), parse_mode='Markdown')

# --- 🚨 DIRECT CHAT LOGIC 🚨 ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
def handle_all_messages(message):
    # Check if ADMIN_ID is set
    if not ADMIN_ID:
        bot.reply_to(message, "❌ Admin is currently offline (ID not set).")
        return

    # 1. Admin ka reply (Admin -> User)
    if str(message.from_user.id) == str(ADMIN_ID):
        if message.reply_to_message:
            try:
                # Forwarded message se user ki ID nikalna
                text = message.reply_to_message.text or message.reply_to_message.caption
                target_user_id = text.split('\n')[0].replace("📩 New Message from ID: ", "").strip()
                
                bot.send_message(target_user_id, "👨‍💻 *Admin Reply:* \n\n" + message.text, parse_mode='Markdown')
                bot.send_message(ADMIN_ID, "✅ Reply sent!")
            except:
                bot.send_message(ADMIN_ID, "❌ Error: Use 'Reply' on user's message.")
        return

    # 2. User ka message (User -> Admin)
    user_info = f"📩 New Message from ID: {message.chat.id}\n👤 Name: {message.from_user.first_name}\n\n"
    
    try:
        if message.text:
            bot.send_message(ADMIN_ID, user_info + "💬 Message: " + message.text)
        elif message.photo:
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=user_info + "🖼 Photo attached")
        
        bot.reply_to(message, "✅ Aapka message Admin ko bhej diya gaya hai. Wait kijiye.")
    except Exception as e:
        bot.reply_to(message, "❌ Message forwarding failed. Admin ID might be wrong.")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
