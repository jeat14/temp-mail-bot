from telegram.ext import Application, CommandHandler
import random
import os
import string
from datetime import datetime
import requests  # Changed to regular requests instead of aiohttp

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

DOMAINS = [
    "1secmail.com",
    "1secmail.org",
    "1secmail.net"
]

def generate_random_string(length=10):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

async def start(update, context):
    await update.message.reply_text("Commands:\n/gen - Generate new email\n/check - Check messages\n/list - Show emails")

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
            'created': datetime.now()
        }
        
        context.user_data['emails'].append(email_data)
        
        response = f"📧 New email created!\n\nEmail: {email}\n\nUse /check to see messages"
        await update.message.reply_text(response)
        
    except Exception as e:
        print(f"Debug - Error: {str(e)}")
        await update.message.reply_text("Error generating email. Please try again.")

async def list_emails(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("No emails yet. Use /gen to create one.")
        return
    
    msg = "📧 Your active emails:\n\n"
    for i, email in enumerate(context.user_data['emails'], 1):
        created_time = email['created'].strftime("%H:%M:%S")
        msg += f"{i}. {email['address']}\n"
        msg += f"   Created at: {created_time}\n\n"
    
    await update.message.reply_text(msg)

async def check_messages(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("No emails yet. Use /gen to create one.")
        return
    
    email = context.user_data['emails'][-1]
    login = email['login']
    domain = email['domain']
    
    try:
        # Using regular requests instead of aiohttp
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
        response = requests.get(url)
        
        if response.status_code == 200:
            messages = response.json()
            
            if not messages:
                await update.message.reply_text(f"📭 No messages yet for {email['address']}")
                return
            
            msg = f"📬 Inbox for {email['address']}:\n\n"
            for i, message in enumerate(messages, 1):
                # Get message content
                msg_id = message['id']
                content_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}"
                content_response = requests.get(content_url)
                
                if content_response.status_code == 200:
                    content = content_response.json()
                    msg += f"📧 Message {i}:\n"
                    msg += f"From: {content.get('from', 'Unknown')}\n"
                    msg += f"Subject: {content.get('subject', 'No subject')}\n"
                    msg += f"Date: {content.get('date', 'Unknown')}\n"
                    if content.get('textBody'):
                        body = content['textBody'].replace('\r', '').replace('\n', ' ')[:200]
                        msg += f"Body: {body}...\n\n"
            
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("No messages found.")
            
    except Exception as e:
        print(f"Debug error: {str(e)}")
        await update.message.reply_text(f"📭 No messages yet for {email['address']}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", generate_email))
    app.add_handler(CommandHandler("list", list_emails))
    app.add_handler(CommandHandler("check", check_messages))
    
    print("Bot starting...")
    app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url="https://temp-mail-bot-j4bi.onrender.com")

if __name__ == "__main__":
    main()
