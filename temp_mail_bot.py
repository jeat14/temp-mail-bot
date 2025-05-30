cat << 'EOF' > temp_mail_bot.py
from telegram.ext import Application, CommandHandler
import random
import string
import os
from datetime import datetime, timedelta
import re

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

DOMAINS = ['tempmail.com', 'throwaway.com', 'tempbox.net', 
'quickmail.org']
EXPIRATION_MINUTES = 10

async def start(update, context):
    await update.message.reply_text("Bot Commands: /gen /custom /list 
/check /time /del")

def generate_random_string(length=10):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

async def gen(update, context):
    random_name = generate_random_string()
    domain = random.choice(DOMAINS)
    email = f"{random_name}@{domain}"
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
    email_data = {'address': email, 'expires': datetime.now() + 
timedelta(minutes=EXPIRATION_MINUTES), 'messages': []}
    context.user_data['emails'].append(email_data)
    await update.message.reply_text(f"New email: {email}")

async def custom(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /custom yourprefix")
        return
    prefix = context.args[0].lower()
    domain = random.choice(DOMAINS)
    email = f"{prefix}{generate_random_string(5)}@{domain}"
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
    email_data = {'address': email, 'expires': datetime.now() + 
timedelta(minutes=EXPIRATION_MINUTES), 'messages': []}
    context.user_data['emails'].append(email_data)
    await update.message.reply_text(f"Custom email: {email}")

async def list_mail(update, context):
    if 'emails' not in context.user_data or not 
context.user_data['emails']:
        await update.message.reply_text("No emails")
        return
    now = datetime.now()
    active_emails = [e for e in context.user_data['emails'] if 
e['expires'] > now]
    if not active_emails:
        await update.message.reply_text("No active emails")
        return
    msg = "Your emails:\n"
    for i, email in enumerate(active_emails, 1):
        msg += f"{i}. {email['address']}\n"
    await update.message.reply_text(msg)

async def check_messages(update, context):
    if 'emails' not in context.user_data or not 
context.user_data['emails']:
        await update.message.reply_text("No emails")
        return
    now = datetime.now()
    active_emails = [e for e in context.user_data['emails'] if 
e['expires'] > now]
    if not active_emails:
        await update.message.reply_text("All emails expired")
        return
    email = active_emails[-1]
    await update.message.reply_text(f"Checking: {email['address']}")

async def time_command(update, context):
    if 'emails' not in context.user_data or not 
context.user_data['emails']:
        await update.message.reply_text("No emails")
        return
    now = datetime.now()
    active_emails = [e for e in context.user_data['emails'] if 
e['expires'] > now]
    if not active_emails:
        await update.message.reply_text("All emails expired")
        return
    email = active_emails[-1]
    remaining = email['expires'] - now
    minutes = int(remaining.total_seconds() / 60)
    await update.message.reply_text(f"Time left: {minutes} minutes")

async def delete(update, context):
    if 'emails' not in context.user_data or not 
context.user_data['emails']:
        await update.message.reply_text("No emails")
        return
    deleted = context.user_data['emails'].pop()
    await update.message.reply_text(f"Deleted: {deleted['address']}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("custom", custom))
    app.add_handler(CommandHandler("list", list_mail))
    app.add_handler(CommandHandler("check", check_messages))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("del", delete))
    print("Bot starting...")
    app.run_webhook(listen="0.0.0.0", port=PORT, 
webhook_url="https://temp-mail-bot-j4bi.onrender.com")

if __name__ == "__main__":
    main()
EOF

