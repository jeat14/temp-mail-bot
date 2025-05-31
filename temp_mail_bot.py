from telegram.ext import Application, CommandHandler
import random
import os
import string
from datetime import datetime
import aiohttp

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
        
        response = (
            f"📧 New email created!\n\n"
            f"Email: {email}\n\n"
            f"You can now receive emails at this address.\n"
            f"Use /check to see incoming messages."
        )
        
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
        async with aiohttp.ClientSession() as session:
            # First, get the list of messages
            messages_url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
            async with session.get(messages_url) as response:
                messages = await response.json()
                
                if not messages:
                    await update.message.reply_text(f"📭 No messages yet for {email['address']}")
                    return
                
                # If we have messages, get the content of each
                msg = f"📬 Inbox for {email['address']}:\n\n"
                for i, message in enumerate(messages, 1):
                    message_id = message['id']
                    content_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={message_id}"
                    
                    async with session.get(content_url) as content_response:
                        content = await content_response.json()
                        
                        msg += f"📧 Message {i}:\n"
                        msg += f"From: {content.get('from')}\n"
                        msg += f"Subject: {content.get('subject')}\n"
                        msg += f"Date: {content.get('date')}\n"
                        if content.get('textBody'):
                            body = content['textBody']
                            # Limit body length and remove any problematic characters
                            body = body.replace('\r', '').replace('\n', ' ')[:200]
                            msg += f"Body: {body}...\n\n"
                
                await update.message.reply_text(msg)
                
    except Exception as e:
        print(f"Debug error: {str(e)}")
        await update.message.reply_text("Error checking messages. Please try again.")

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
