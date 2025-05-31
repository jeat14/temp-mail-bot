from telegram.ext import Application, CommandHandler
import random
import string
from datetime import datetime, timedelta
import requests
import os
from aiohttp import web

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

DOMAINS = ["1secmail.com", "1secmail.org", "1secmail.net"]
EMAIL_LIFETIME = 10

routes = web.RouteTableDef()

@routes.get('/')
async def handle_root(request):
    return web.Response(text="Bot is running!", status=200)

@routes.post('/')
async def handle_post(request):
    return web.Response(text="OK", status=200)

def generate_random_string(length=10):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

async def start(update, context):
    await update.message.reply_text("Commands: /gen /check /list /time")

async def generate_email(update, context):
    username = generate_random_string(10)
    domain = random.choice(DOMAINS)
    email = f"{username}@{domain}"
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
    email_data = {'address': email, 'login': username, 'domain': domain, 'created': datetime.now(), 'expires': datetime.now() + timedelta(minutes=EMAIL_LIFETIME)}
    context.user_data['emails'].append(email_data)
    await update.message.reply_text(f"New email: {email}")

async def list_emails(update, context):
    if not context.user_data.get('emails'):
        await update.message.reply_text("No emails")
        return
    now = datetime.now()
    active_emails = []
    for email in context.user_data['emails']:
        if email['expires'] > now:
            active_emails.append(email)
    if not active_emails:
        await update.message.reply_text("No active emails")
        return
    msg = "Your emails:"
    for i, email in enumerate(active_emails, 1):
        remaining = email['expires'] - now
        minutes = int(remaining.total_seconds() / 60)
        msg += f"\n{i}. {email['address']}"
        msg += f"\nTime: {minutes}m"
    await update.message.reply_text(msg)

async def check_messages(update, context):
    try:
        if not context.user_data.get('emails'):
            await update.message.reply_text("No emails")
            return

        now = datetime.now()
        active_emails = [e for e in context.user_data['emails'] if e['expires'] > now]
        
        if not active_emails:
            await update.message.reply_text("No active emails")
            return
            
        email = active_emails[-1]
        await update.message.reply_text(f"Checking {email['address']}...")
        
        # Get messages
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={email['login']}&domain={email['domain']}"
        messages = requests.get(url).json()
        
        if not messages:
            await update.message.reply_text(f"No messages found for {email['address']}")
            return
            
        # Get message details
        msg = f"Messages for {email['address']}:"
        for i, message in enumerate(messages, 1):
            msg_id = message['id']
            msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={email['login']}&domain={email['domain']}&id={msg_id}"
            content = requests.get(msg_url).json()
            msg += f"\n\nMessage {i}:"
            msg += f"\nFrom: {content.get('from', 'Unknown')}"
            msg += f"\nSubject: {content.get('subject', 'No subject')}"
            
        await update.message.reply_text(msg)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        await update.message.reply_text(f"No messages found for {email['address']}")

async def check_time(update, context):
    if not context.user_data.get('emails'):
        await update.message.reply_text("No emails")
        return
    now = datetime.now()
    active_emails = []
    for email in context.user_data['emails']:
        if email['expires'] > now:
            active_emails.append(email)
    if not active_emails:
        await update.message.reply_text("No active emails")
        return
    msg = "Time remaining:"
    for i, email in enumerate(active_emails, 1):
        remaining = email['expires'] - now
        minutes = int(remaining.total_seconds() / 60)
        msg += f"\n{i}. {email['address']}: {minutes}m"
    await update.message.reply_text(msg)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", generate_email))
    app.add_handler(CommandHandler("list", list_emails))
    app.add_handler(CommandHandler("check", check_messages))
    app.add_handler(CommandHandler("time", check_time))
    
    print("Starting...")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url="https://temp-mail-bot-j4bi.onrender.com"
    )

if __name__ == "__main__":
    main()
