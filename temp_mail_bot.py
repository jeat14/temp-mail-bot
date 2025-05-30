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
    await update.message.reply_text("Commands: /gen - New email (10min), 
/custom - Custom email, /list - Show emails, /check - Check messages, 
/time - Check time, /del - Delete email")

def generate_random_string(length=10):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def get_time_remaining(email_data):
    now = datetime.now()
    if 'expires' not in email_data:
        return "Expired"
    remaining = email_data['expires'] - now
    minutes = int(remaining.total_seconds() / 60)
    seconds = int(remaining.total_seconds() % 60)
    if remaining.total_seconds() <= 0:
        return "Expired"
    return f"{minutes}m {seconds}s"

async def gen(update, context):
    random_name = generate_random_string()
    domain = random.choice(DOMAINS)
    email = f"{random_name}@{domain}"
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
    now = datetime.now()
    context.user_data['emails'] = [e for e in context.user_data['emails'] 
if e.get('expires', now) > now]
    email_data = {
        'address': email,
        'created': datetime.now(),
        'expires': datetime.now() + timedelta(minutes=EXPIRATION_MINUTES),
        'messages': []
    }
    context.user_data['emails'].append(email_data)
    await update.message.reply_text(f"New email: {email}\nExpires in: 
{EXPIRATION_MINUTES} minutes\nUse /check for messages")

async def custom(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /custom yourprefix")
        return
    prefix = context.args[0].lower()
    if not re.match("^[a-z0-9_-]+$", prefix):
        await update.message.reply_text("Prefix can only contain letters, 
numbers, underscore and dash")
        return
    if len(prefix) < 3:
        await update.message.reply_text("Prefix must be at least 3 
characters")
        return
    domain = random.choice(DOMAINS)
    email = f"{prefix}{generate_random_string(5)}@{domain}"
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
    now = datetime.now()
    context.user_data['emails'] = [e for e in context.user_data['emails'] 
if e.get('expires', now) > now]
    email_data = {
        'address': email,
        'created': datetime.now(),
        'expires': datetime.now() + timedelta(minutes=EXPIRATION_MINUTES),
        'messages': []
    }
    context.user_data['emails'].append(email_data)
    await update.message.reply_text(f"Custom email: {email}\nExpires in: 
{EXPIRATION_MINUTES} minutes")

async def list_mail(update, context):
    if 'emails' not in context.user_data:
        await update.message.reply_text("No emails")
        return
    now = datetime.now()
    context.user_data['emails'] = [e for e in context.user_data['emails'] 
if e.get('expires', now) > now]
    if not context.user_data['emails']:
        await update.message.reply_text("No active emails")
        return
    response = "Your emails:\n\n"
    for idx, email in enumerate(context.user_data['emails'], 1):
        response += f"{idx}. {email['address']}\n"
        response += f"Time left: {get_time_remaining(email)}\n"
        response += f"Messages: {len(email['messages'])}\n\n"
    await update.message.reply_text(response)

async def check_messages(update, context):
    if 'emails' not in context.user_data:
        await update.message.reply_text("Generate an email first using 
/gen")
        return
    now = datetime.now()
    context.user_data['emails'] = [e for e in context.user_data['emails'] 
if e.get('expires', now) > now]
    if not context.user_data['emails']:
        await update.message.reply_text("All emails expired. Use /gen")
        return
    email = context.user_data['emails'][-1]
    if random.random() < 0.3:
        new_message = {
            'from': f"user{random.randint(1000,9999)}@example.com",
            'subject': f"Test message {len(email['messages']) + 1}",
            'time': datetime.now()
        }
        email['messages'].append(new_message)
    response = f"Checking {email['address']}\n"
    response += f"Time left: {get_time_remaining(email)}\n\n"
    if not email['messages']:
        response += "No messages yet"
    else:
        response += "Messages:\n\n"
        for idx, msg in enumerate(email['messages'], 1):
            response += f"{idx}. From: {msg['from']}\n"
            response += f"Subject: {msg['subject']}\n"
            response += f"Time: {msg['time'].strftime('%H:%M:%S')}\n\n"
    await update.message.reply_text(response)

async def time_command(update, context):
    if 'emails' not in context.user_data:
        await update.message.reply_text("No active emails")
        return
    now = datetime.now()
    context.user_data['emails'] = [e for e in context.user_data['emails'] 
if e.get('expires', now) > now]
    if not context.user_data['emails']:
        await update.message.reply_text("All emails expired")
        return
    response = "Time remaining:\n\n"
    for idx, email in enumerate(context.user_data['emails'], 1):
        response += f"{idx}. {email['address']}\n"
        response += f"Time: {get_time_remaining(email)}\n\n"
    await update.message.reply_text(response)

async def delete(update, context):
    if 'emails' not in context.user_data or not 
context.user_data['emails']:
        await update.message.reply_text("No emails to delete")
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
