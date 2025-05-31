from telegram.ext import Application, CommandHandler
import random
import string
from datetime import datetime, timedelta
import requests
import os

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

DOMAINS = ["1secmail.com", "1secmail.org", "1secmail.net"]
EMAIL_LIFETIME = 10

def generate_random_string(length=10):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

async def start(update, context):
    await update.message.reply_text("Commands: /gen /check /list /time")

async def generate_email(update, context):
    try:
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
        await update.message.reply_text(f"New email: {email}")
        
    except Exception as e:
        print(f"Debug - Error: {str(e)}")
        await update.message.reply_text("Error")

async def list_emails(update, context):
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
    
    msg = "Your emails:"
    for i, email in enumerate(active_emails, 1):
        remaining = email['expires'] - now
        minutes = int(remaining.total_seconds() / 60)
        msg += f"\n{i}. {email['address']}"
        msg += f"\nTime: {minutes}m"
    
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
        await update.message.reply_text("No active emails")
        return
    
    email = active_emails[-1]
    login = email['login']
    domain = email['domain']
    
    try:
        url = 
f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
        response = requests.get(url)
        
        if response.status_code == 200:
            messages = response.json()
            
            if not messages:
                await update.message.reply_text(f"No messages for 
{email['address']}")
                return
            
            msg = f"Messages for {email['address']}:"
            for i, message in enumerate(messages, 1):
                msg_id = message['id']
                content_url = 
f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}"
                content_response = requests.get(content_url)
                
                if content_response.status_code == 200:
                    content = content_response.json()
                    msg += f"\n\nMessage {i}:"
                    msg += f"\nFrom: {content.get('from', 'Unknown')}"
                    msg += f"\nSubject: {content.get('subject', 'No 
subject')}"
            
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("Error checking messages")
            
    except Exception as e:
        print(f"Debug error: {str(e)}")
        await update.message.reply_text("Error")

async def check_time(update, context):
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
        webhook_url="https://temp-mail-bot-j4bi.onrender.com/" + TOKEN
    )

if __name__ == "__main__":
    main()

