import telebot
import google.generativeai as genai
import PIL.Image
import io
import os
from flask import Flask
from threading import Thread

# 🚨 CONFIGURATION 🚨
# Github par code dalte waqt Token yahan mat likhna, Render ke 'Environment Variables' mein dalo
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8611431269:AAFqZvDTt7W8riHh5f87Lxi1NU3jj3npkwc')
GEMINI_KEY = os.getenv('GEMINI_KEY', 'AIzaSyDFnJUW5EqB8DYTqrbDbYgNFURp-O9b-6w')

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Flask server bot ko zinda rakhne ke liye
app = Flask('')

@app.route('/')
def home():
    return "Bot is Alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

SYSTEM_PROMPT = "You are AI Support of Esports Arena India. Min Withdraw: 50, Min Deposit: 10, Level: 25+. Be polite."

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "👋 Namaste! Esports Arena AI Support 24/7 live hai. Problem likhien ya Screenshot bhejien.")

@bot.message_handler(content_types=['text'])
def handle_text(message):
    try:
        response = model.generate_content(f"{SYSTEM_PROMPT}\nUser: {message.text}")
        bot.reply_to(message, response.text, parse_mode='Markdown')
    except:
        bot.reply_to(message, "AI Busy hai, thodi der baad bhejien.")

@bot.message_handler(content_types=['photo'])
def handle_image(message):
    bot.reply_to(message, "🔍 Analyzing screenshot...")
    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        img = PIL.Image.open(io.BytesIO(downloaded_file))
        response = model.generate_content([f"{SYSTEM_PROMPT}\nAnalyze this screenshot:", img])
        bot.reply_to(message, response.text, parse_mode='Markdown')
    except:
        bot.reply_to(message, "Photo load nahi hui.")

if __name__ == "__main__":
    keep_alive()  # Web server start
    print("🚀 Bot is running 24/7...")
    bot.polling(none_stop=True)
