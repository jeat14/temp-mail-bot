from telegram.ext import Application, CommandHandler
import random
import string
from datetime import datetime
import requests

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"

DOMAINS = ["1secmail.com", "1secmail.org", "1secmail.net"]

def generate_random_string(length=10):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

async def start(update, context):
    await update.message.reply_text("Commands: /gen - New email, /check - Check messages, /list - Show emails")

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
        await update.message.reply_text(f"New email: {email}")
        
    except Exception as e:
        print(f"Debug - Error: {str(e)}")
        await update.message.reply_text("Error generating email. Please try again.")

async def list_emails(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("No emails yet. Use /gen to create one.")
        return
    
    msg = "Your emails:"
    for i, email in enumerate(context.user_data['emails'], 1):
        created_time = email['created'].strftime("%H:%M:%S")
        msg += f"\n{i}. {email['address']}"
        msg += f"\nCreated: {created_time}\n"
    
    await update.message.reply_text(msg)

async def check_messages(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("No emails yet. Use /gen to create one.")
        return
    
    email = context.user_data['emails'][-1]
    login = email['login']
    domain = email['domain']
    
    try:
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
        response = requests.get(url)
        
        if response.status_code == 200:
            messages = response.json()
            
            if not messages:
                await update.message.reply_text(f"No messages for {email['address']}")
                return
            
            msg = f"Inbox for {email['address']}:"
            for i, message in enumerate(messages, 1):
                msg_id = message['id']
                content_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}"
                content_response = requests.get(content_url)
                
                if content_response.status_code == 200:
                    content = content_response.json()
                    msg += f"\n\nMessage {i}:"
                    msg += f"\nFrom: {content.get('from', 'Unknown')}"
                    msg += f"\nSubject: {content.get('subject', 'No subject')}"
                    msg += f"\nDate: {content.get('date', 'Unknown')}"
                    if content.get('textBody'):
                        body = content['textBody'].replace('\r', '').replace('\n', ' ')[:200]
                        msg += f"\nBody: {body}..."
            
            await update.message.reply_text(msg)
        else:
            await update.message.reply_text("No messages found.")
            
    except Exception as e:
        print(f"Debug error: {str(e)}")
        await update.message.reply_text(f"No messages yet for {email['address']}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", generate_email))
    app.add_handler(CommandHandler("list", list_emails))
    app.add_handler(CommandHandler("check", check_messages))
    
    print("Bot starting...")
    app.run_polling(poll_interval=1)

if __name__ == "__main__":
    main()
