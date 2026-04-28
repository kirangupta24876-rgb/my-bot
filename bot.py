import telebot
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread

# 🚨 AB KOI KEY YAHAN NAHI LIKHNI HAI 🚨
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_KEY = os.environ.get('GEMINI_KEY')

if not TELEGRAM_TOKEN or not GEMINI_KEY:
    print("Error: API Keys not found in environment variables!")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Baaki ka poora code (Flask aur Handlers) same rahega...
# ... (Wahi purana code niche dalo) ...

app = Flask('')
@app.route('/')
def home(): return "Bot is Alive!"
def run(): app.run(host='0.0.0.0', port=8080)
def keep_alive(): Thread(target=run).start()

SYSTEM_PROMPT = "You are AI Support of Esports Arena India. Min Withdraw: 50, Min Deposit: 10, Level: 25+. Be polite."

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Namaste! AI Support Active hai.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        response = model.generate_content(f"{SYSTEM_PROMPT}\nUser: {message.text}")
        bot.reply_to(message, response.text, parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(message, "AI thoda busy hai, baad mein try karein.")

if __name__ == "__main__":
    keep_alive()
    bot.polling(none_stop=True)
