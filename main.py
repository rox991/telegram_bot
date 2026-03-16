import os
import threading
import telebot
from flask import Flask
from openai import OpenAI

# 1. Fetch Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
HF_TOKEN = os.environ.get("HF_TOKEN")

if not BOT_TOKEN or not HF_TOKEN:
    raise ValueError("Missing BOT_TOKEN or HF_TOKEN environment variables.")

# 2. Initialize Telegram Bot and OpenAI Client
bot = telebot.TeleBot(BOT_TOKEN)
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=HF_TOKEN,
)

# 3. Handle incoming Telegram messages
@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Query the Hugging Face router via OpenAI python package
        chat_completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1:novita",
            messages=[
                {
                    "role": "user",
                    "content": message.text,
                },
            ],
        )
        
        # Extract the response text
        reply_text = chat_completion.choices[0].message.content
        
        # Send back to the user
        bot.reply_to(message, reply_text)
        
    except Exception as e:
        error_msg = f"Sorry, an error occurred: {str(e)}"
        bot.reply_to(message, error_msg)
        print(error_msg)

# 4. Flask Web Server (Required for Render.com to keep the app alive)
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is running successfully!", 200

# Function to run the bot polling in a separate thread
def run_bot():
    print("Starting Telegram Bot...")
    bot.infinity_polling()

if __name__ == "__main__":
    # Start the bot in a background thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()
    
    # Start the Flask web server on the main thread
    # Render provides the PORT environment variable dynamically
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting Flask server on port {port}...")
    app.run(host="0.0.0.0", port=port)
