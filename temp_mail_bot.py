echo 'from telegram.ext import Application, CommandHandler
import random
import string
import os
from datetime import datetime, timedelta

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

DOMAINS = ["tempmail.com", "throwaway.com"]

async def start(update, context):
    await update.message.reply_text("Commands: /gen /custom /list /check")

async def gen(update, context):
    email = f"user{random.randint(1000,9999)}@{random.choice(DOMAINS)}"
    if "emails" not in context.user_data:
        context.user_data["emails"] = []
    context.user_data["emails"].append(email)
    await update.message.reply_text(f"New email: {email}")

async def custom(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /custom yourprefix")
        return
    prefix = context.args[0]
    email = f"{prefix}{random.randint(100,999)}@{random.choice(DOMAINS)}"
    if "emails" not in context.user_data:
        context.user_data["emails"] = []
    context.user_data["emails"].append(email)
    await update.message.reply_text(f"Custom email: {email}")

async def list_mail(update, context):
    if "emails" not in context.user_data or not 
context.user_data["emails"]:
        await update.message.reply_text("No emails")
        return
    msg = "Your emails:\\n"
    for i, email in enumerate(context.user_data["emails"], 1):
        msg += f"{i}. {email}\\n"
    await update.message.reply_text(msg)

async def check(update, context):
    if "emails" not in context.user_data or not 
context.user_data["emails"]:
        await update.message.reply_text("No emails")
        return
    email = context.user_data["emails"][-1]
    await update.message.reply_text(f"Checking: {email}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("custom", custom))
    app.add_handler(CommandHandler("list", list_mail))
    app.add_handler(CommandHandler("check", check))
    print("Bot starting...")
    app.run_webhook(listen="0.0.0.0", port=PORT, 
webhook_url="https://temp-mail-bot-j4bi.onrender.com")

if __name__ == "__main__":
    main()' > temp_mail_bot.py

