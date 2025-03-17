import argparse
import traceback
import asyncio
import re
import telebot
from telebot.async_telebot import AsyncTeleBot
import handlers
from config import conf, generation_config, safety_settings

import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

# Get tokens from environment variables
tg_token = os.getenv("TELEGRAM_BOT_API_KEY")
gemini_key = os.getenv("GEMINI_API_KEY")

if not tg_token or not gemini_key:
    print("Error: Please set TELEGRAM_BOT_API_KEY and GEMINI_API_KEY environment variables")
    sys.exit(1)
    
print("Environment variables loaded.")


async def main():
    # Init bot
    bot = AsyncTeleBot(tg_token)
    await bot.delete_my_commands(scope=None, language_code=None)
    await bot.set_my_commands(
    commands=[
        telebot.types.BotCommand("start", "Start"),
        telebot.types.BotCommand("memex", "using gemini-2.0-flash-exp"),
        telebot.types.BotCommand("gemini_pro", "using gemini-1.5-pro"),
        telebot.types.BotCommand("draw", "draw picture"),
        telebot.types.BotCommand("edit", "edit photo"),
        telebot.types.BotCommand("clear", "Clear all history"),
        telebot.types.BotCommand("switch","switch default model")
    ],
)
    print("Bot init done.")

    # Init commands
    bot.register_message_handler(handlers.start,                         commands=['start'],         pass_bot=True)
    bot.register_message_handler(handlers.gemini_stream_handler,         commands=['memex'],        pass_bot=True)
    bot.register_message_handler(handlers.gemini_pro_stream_handler,     commands=['gemini_pro'],    pass_bot=True)
    bot.register_message_handler(handlers.draw_handler,                  commands=['draw'],          pass_bot=True)
    bot.register_message_handler(handlers.gemini_edit_handler,           commands=['edit'],          pass_bot=True)
    bot.register_message_handler(handlers.clear,                         commands=['clear'],         pass_bot=True)
    bot.register_message_handler(handlers.switch,                        commands=['switch'],        pass_bot=True)
    bot.register_message_handler(handlers.gemini_photo_handler,          content_types=["photo"],    pass_bot=True)
    bot.register_message_handler(
        handlers.gemini_private_handler,
        func=lambda message: message.chat.type == "private",
        content_types=['text'],
        pass_bot=True)

    # Start bot
    print("Starting Gemini_Telegram_Bot.")
    try:
        # Keep the bot running
        print("Bot is running...")
        await bot.polling(non_stop=True, timeout=60)
    except Exception as e:
        print(f"Bot polling error: {e}")
        traceback.print_exc()

if __name__ == '__main__':
    try:
        web_thread = Thread(target=run_web)
        web_thread.start()
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped gracefully")
    except Exception as e:
        print(f"Error occurred: {e}")
        traceback.print_exc()