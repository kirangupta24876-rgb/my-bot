import telebot
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# API Keys from Render Environment Variables
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# Init AI & Bot
genai.configure(api_key=GEMINI_KEY)
# Safety settings set to BLOCK_NONE to avoid "AI Busy" errors on gaming terms
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    safety_settings={
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
    }
)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

SYSTEM_PROMPT = "You are the Official AI Support of Esports Arena India. Rules: Min Withdraw ₹50, Min Deposit ₹10, ID shared 15 min before match. Be helpful."

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Namaste! Esports Arena AI Support active hai. Puchhiye apna sawal.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        response = model.generate_content(f"{SYSTEM_PROMPT}\nUser: {message.text}")
        bot.reply_to(message, response.text, parse_mode='Markdown')
    except Exception as e:
        # 🚨 Detailed error report to find the cause
        error_msg = str(e)
        if "429" in error_msg:
            bot.reply_to(message, "⚠️ Daily limit khatam ho gayi hai (Google Free Limit). Kal dobara try karein!")
        elif "API_KEY_INVALID" in error_msg:
            bot.reply_to(message, "⚠️ API Key galat hai. Render settings mein nayi key dalein.")
        else:
            print(f"Error: {e}")
            bot.reply_to(message, "AI thoda thaka hua hai, 1 min baad message karein.")

if __name__ == "__main__":
    keep_alive()
    print("✅ Bot is Starting...")
    bot.polling(none_stop=True)
