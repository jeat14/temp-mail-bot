from telegram.ext import Application, CommandHandler
import random
import os
import string
from datetime import datetime
import requests
from aiohttp import web

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

DOMAINS = [
    "1secmail.com",
    "1secmail.org",
    "1secmail.net"
]

# Add web routes
async def web_app(request):
    return web.Response(text="Temp Mail Bot is running!")

# Rest of your existing code...
[previous code remains the same until main()]

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", generate_email))
    app.add_handler(CommandHandler("list", list_emails))
    app.add_handler(CommandHandler("check", check_messages))
    
    # Add web app
    web_app = web.Application()
    web_app.router.add_get('/', web_app)
    
    print("Bot starting...")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url="https://temp-mail-bot-j4bi.onrender.com",
        webhook_app=web_app
    )

if __name__ == "__main__":
    main()
