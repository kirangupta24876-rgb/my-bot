import telebot
from telebot import types
import os
from flask import Flask
from threading import Thread

# 🚨 CONFIGURATION 🚨
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
# Render ke Environment Variables mein ADMIN_ID naam se apni ID dalo
ADMIN_ID = os.environ.get('ADMIN_ID') 

bot = telebot.TeleBot(TELEGRAM_TOKEN)

app = Flask('')
@app.route('/')
def home(): return "Direct Support Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

# --- MAIN MENU ---
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
    welcome_text = (
        "👋 *Namaste " + message.from_user.first_name + "!*\n\n"
        "Main Esports Arena ka official helper hoon.\n"
        "Agar aapko mujhse direct baat karni hai, toh bas apni problem yahan *Type* karke bhej dijiye."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=main_menu(), parse_mode='Markdown')

# --- 🚨 DIRECT CHAT LOGIC (Forward to Admin) 🚨 ---
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'video'])
def handle_all_messages(message):
    # Agar Admin ne reply kiya hai (User ko message bhejne ke liye)
    if str(message.from_user.id) == str(ADMIN_ID):
        if message.reply_to_message:
            try:
                # Original user ki ID nikalna forwarded message se
                # Humne format niche set kiya hai: "USER_ID: [id]"
                lines = message.reply_to_message.text.split('\n')
                target_user_id = lines[0].replace("📩 New Message from ID: ", "").strip()
                
                bot.send_message(target_user_id, "👨‍💻 *Admin Reply:* \n\n" + message.text, parse_mode='Markdown')
                bot.send_message(ADMIN_ID, "✅ Reply sent successfully!")
            except Exception as e:
                bot.send_message(ADMIN_ID, "❌ Error: Could not send reply. Make sure you reply to the bot's notification.")
        return

    # Agar User ne message bheja hai (Admin ko forward karne ke liye)
    user_info = f"📩 New Message from ID: {message.chat.id}\n👤 Name: {message.from_user.first_name}\n\n"
    
    if message.text:
        bot.send_message(ADMIN_ID, user_info + "💬 Text: " + message.text)
    elif message.photo:
        bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=user_info + "🖼 Photo attached")
    
    bot.reply_to(message, "✅ Aapka message Admin ko bhej diya gaya hai. Kripya reply ka intezar karein.")

# --- BUTTON CLICKS ---
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == "chat_admin":
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "✍️ *Apni problem yahan type karein:* \n(Aap screenshot bhi bhej sakte hain)")
        return

    # Baaki buttons ke replies (Wahi purana logic)
    replies = {
        "deposit": "💰 *DEPOSIT HELP*\n\nMinimum ₹10. Payment ke baad 5 min wait karein. Agar na aaye toh Transaction ID bhejien.",
        "withdraw": "💸 *WITHDRAWAL*\n\nMinimum ₹50. 24 hours ke andar payment mil jayegi.",
        "roomid": "🔑 *ROOM ID*\n\nMatch se 15 min pehle 'LIVE' tab mein dekhein.",
        "rules": "📋 *RULES*\n\nLevel 25+ only. No Hacks/Emulators. Screen recording must.",
        "refer": "🤝 *REFER*\n\nRefer friends to earn ₹10 bonus cash."
    }
    
    text = replies.get(call.data, "Neeche diye gaye buttons use karein:")
    back = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅️ Back", callback_data='main_menu'))
    
    if call.data == "main_menu":
        bot.edit_message_text("Problem chuniye:", call.message.chat.id, call.message.message_id, reply_markup=main_menu())
    else:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=back, parse_mode='Markdown')

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
