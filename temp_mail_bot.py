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
    return web.Response(text="Bot is running!")

def generate_random_string(length=10):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

async def start(update, context):
    await update.message.reply_text("Commands:\n/gen - Create new email\n/check - Check messages\n/list - Show emails\n/time - Check time left")

async def generate_email(update, context):
    username = generate_random_string(10)
    domain = random.choice(DOMAINS)
    email = f"{username}@{domain}"
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
    email_data = {
        'address': email,
        'login': username,
        'domain': domain,
        'created': datetime.now(),
        'expires': datetime.now() + timedelta(minutes=EMAIL_LIFETIME)
    }
    context.user_data['emails'].append(email_data)
    await update.message.reply_text(f"New email created: {email}\nUse /check to see messages")

async def list_emails(update, context):
    if not context.user_data.get('emails'):
        await update.message.reply_text("No emails yet. Use /gen to create one.")
        return
    
    now = datetime.now()
    active_emails = []
    for email in context.user_data['emails']:
        if email['expires'] > now:
            active_emails.append(email)
    
    if not active_emails:
        await update.message.reply_text("No active emails. Use /gen to create one.")
        return
    
    msg = "Your active emails:"
    for i, email in enumerate(active_emails, 1):
        remaining = email['expires'] - now
        minutes = int(remaining.total_seconds() / 60)
        msg += f"\n\n{i}. {email['address']}"
        msg += f"\nTime left: {minutes} minutes"
    
    await update.message.reply_text(msg)

async def check_messages(update, context):
    try:
        if not context.user_data.get('emails'):
            await update.message.reply_text("No emails yet. Use /gen to create one.")
            return
        
        now = datetime.now()
        active_emails = []
        for email in context.user_data['emails']:
            if email['expires'] > now:
                active_emails.append(email)
        
        if not active_emails:
            await update.message.reply_text("All emails expired. Use /gen to create new one.")
            return
        
        email = active_emails[-1]
        login = email['login']
        domain = email['domain']
        
        await update.message.reply_text(f"Checking messages for {email['address']}...")
        
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        messages = response.json()
        
        if not messages:
            remaining = email['expires'] - now
            minutes = int(remaining.total_seconds() / 60)
            await update.message.reply_text(f"No messages yet for {email['address']}\nEmail expires in: {minutes} minutes")
            return
        
        msg = f"📬 Inbox for {email['address']}:"
        for i, message in enumerate(messages, 1):
            msg_id = message['id']
            content_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}"
            content_response = requests.get(content_url, timeout=10)
            content_response.raise_for_status()
            
            content = content_response.json()
            msg += f"\n\n📧 Message {i}:"
            msg += f"\nFrom: {content.get('from', 'Unknown')}"
            msg += f"\nSubject: {content.get('subject', 'No subject')}"
            if content.get('textBody'):
                body = content['textBody'].replace('\r', '').replace('\n', ' ')[:200]
                msg += f"\nBody: {body}..."
        
        remaining = email['expires'] - now
        minutes = int(remaining.total_seconds() / 60)
        msg += f"\n\n⏱ Email expires in: {minutes} minutes"
        
        await update.message.reply_text(msg)
        
    except requests.exceptions.RequestException as e:
        print(f"API Error: {str(e)}")
        await update.message.reply_text(f"Checking messages for {email['address']}... No messages found.")
    except Exception as e:
        print(f"Error: {str(e)}")
        await update.message.reply_text("Error checking messages. Please try again.")

async def check_time(update, context):
    if not context.user_data.get('emails'):
        await update.message.reply_text("No emails yet. Use /gen to create one.")
        return
    
    now = datetime.now()
    active_emails = []
    for email in context.user_data['emails']:
        if email['expires'] > now:
            active_emails.append(email)
    
    if not active_emails:
        await update.message.reply_text("All emails expired. Use /gen to create new one.")
        return
    
    msg = "⏱ Time remaining:"
    for i, email in enumerate(active_emails, 1):
        remaining = email['expires'] - now
        minutes = int(remaining.total_seconds() / 60)
        msg += f"\n\n{i}. {email['address']}"
        msg += f"\n{minutes} minutes left"
    
    await update.message.reply_text(msg)

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", generate_email))
    app.add_handler(CommandHandler("list", list_emails))
    app.add_handler(CommandHandler("check", check_messages))
    app.add_handler(CommandHandler("time", check_time))
    
    web_app = web.Application()
    web_app.add_routes(routes)
    
    print("Starting...")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url="https://temp-mail-bot-j4bi.onrender.com"
    )

if __name__ == "__main__":
    main()
