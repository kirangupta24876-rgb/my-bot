import telebot
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# 🚨 API Keys - Render ke Environment Variables se uthayega
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

# Google Gemini Setup
genai.configure(api_key=GEMINI_KEY)

# 🚨 SAFETY SETTINGS: Isse "AI Thaka hua hai" wala error 90% khatam ho jayega
safe = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

model = genai.GenerativeModel(model_name='gemini-1.5-flash', safety_settings=safe)
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Web Server Render ko zinda rakhne ke liye
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

SYSTEM_PROMPT = """
You are the Support Assistant of 'Esports Arena India'.
App Rules: Min Withdraw ₹50, Min Deposit ₹10, Level 25+ required.
Reply in Hinglish (Hindi + English). Be a professional support agent.
"""

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Namaste! Esports Arena AI Support active hai. Apna sawal likhiye.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        # AI se response mangna
        response = model.generate_content(f"{SYSTEM_PROMPT}\nUser: {message.text}")
        bot.reply_to(message, response.text, parse_mode='Markdown')
    except Exception as e:
        # 🚨 ASLI ERROR CHECK KARNE KE LIYE 🚨
        error_msg = str(e)
        if "429" in error_msg:
            bot.reply_to(message, "⚠️ Limit Khatam! Google AI free mein ek minute mein kuch hi reply deta hai. 1 minute baad try karein.")
        elif "API_KEY_INVALID" in error_msg:
            bot.reply_to(message, "❌ API Key galat hai! Render settings mein nayi Gemini key dalein.")
        else:
            bot.reply_to(message, f"❌ AI Error: {error_msg[:100]}") # Asli error dikhayega

if __name__ == "__main__":
    keep_alive()
    print("✅ Bot is Starting...")
    bot.polling(none_stop=True)
