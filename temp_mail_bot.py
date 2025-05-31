from telegram.ext import Application, CommandHandler
import random
import string
from datetime import datetime, timedelta
import requests
import os
from aiohttp import web
import asyncio

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

DOMAINS = ["1secmail.com", "1secmail.org", "1secmail.net"]
EMAIL_LIFETIME_DAYS = 2

# Web routes
routes = web.RouteTableDef()

@routes.get('/')
async def handle_root(request):
    return web.Response(text="Bot is running!", status=200)

@routes.post('/' + TOKEN)
async def handle_webhook(request):
    return web.Response(status=200)

[rest of your existing bot code]

async def run_bot():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cmds", cmds))
    app.add_handler(CommandHandler("gen", generate_email))
    app.add_handler(CommandHandler("list", list_emails))
    app.add_handler(CommandHandler("check", check_messages))
    app.add_handler(CommandHandler("time", check_time))
    
    await app.initialize()
    await app.start()
    
    # Set webhook
    webhook_url = f"https://temp-mail-bot-j4bi.onrender.com/{TOKEN}"
    await app.bot.set_webhook(webhook_url)
    
    print("Bot started...")
    
    # Keep the bot running
    while True:
        await asyncio.sleep(1)

async def run_webapp():
    app = web.Application()
    app.add_routes(routes)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', PORT)
    await site.start()
    print("Web app started...")

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.create_task(run_bot())
    loop.create_task(run_webapp())
    
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
