from telegram.ext import Application, CommandHandler
import random
import string
from datetime import datetime, timedelta
import requests
import os

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

DOMAINS = ["1secmail.com", "1secmail.org", "1secmail.net"]
EMAIL_LIFETIME_DAYS = 2  # Emails last for 2 days

def generate_random_string(length=10):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

async def start(update, context):
    welcome_msg = """
🤖 *Welcome to TempMail Bot!*

📧 *Available Commands:*
/cmds - Show all commands
/gen - Generate new temporary email
/list - Show your active emails
/check - Check messages
/time - Check remaining time

ℹ️ *How to use:*
1. Use /gen to create a new email
2. Send emails to your temporary address
3. Use /check to see received messages
4. Email expires in 2 days

⏰ Messages are checked every 10 minutes automatically.
"""
    await update.message.reply_text(welcome_msg, parse_mode='Markdown')

async def cmds(update, context):
    commands = """
📋 *Available Commands:*

/start - Start the bot
/cmds - Show this message
/gen - Generate new email
/list - Show active emails
/check - Check messages
/time - Check remaining time

⏰ Emails last for 2 days
📬 Messages checked every 10 minutes
"""
    await update.message.reply_text(commands, parse_mode='Markdown')

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
            'expires': datetime.now() + timedelta(days=EMAIL_LIFETIME_DAYS)
        }
        
        context.user_data['emails'].append(email_data)
        
        response = f"""
✨ *New email created!*

📧 Email: `{email}`
⏱ Expires in: {EMAIL_LIFETIME_DAYS} days
📥 Messages checked every 10 minutes

Use /check to see messages
Use /time to check expiration
"""
        await update.message.reply_text(response, parse_mode='Markdown')
        
    except Exception as e:
        print(f"Debug - Error: {str(e)}")
        await update.message.reply_text("❌ Error generating email. Please try again.")

async def list_emails(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("📭 No emails yet. Use /gen to create one.")
        return
    
    now = datetime.now()
    active_emails = [e for e in context.user_data['emails'] if e['expires'] > now]
    
    if not active_emails:
        await update.message.reply_text("📭 No active emails. Use /gen to create one.")
        return
    
    msg = "📧 *Your active emails:*\n"
    for i, email in enumerate(active_emails, 1):
        remaining = email['expires'] - now
        days = remaining.days
        hours = int(remaining.seconds / 3600)
        msg += f"\n{i}. `{email['address']}`"
        msg += f"\n⏱ Expires in: {days}d {hours}h\n"
    
    await update.message.reply_text(msg, parse_mode='Markdown')

async def check_messages(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("📭 No emails yet. Use /gen to create one.")
        return
    
    now = datetime.now()
    active_emails = [e for e in context.user_data['emails'] if e['expires'] > now]
    
    if not active_emails:
        await update.message.reply_text("📭 All emails expired. Use /gen to create new one.")
        return
    
    email = active_emails[-1]
    login = email['login']
    domain = email['domain']
    
    try:
        url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}"
        response = requests.get(url)
        
        if response.status_code == 200:
            messages = response.json()
            
            if not messages:
                remaining = email['expires'] - now
                days = remaining.days
                hours = int(remaining.seconds / 3600)
                msg = f"📭 No messages for `{email['address']}`\n"
                msg += f"⏱ Email expires in: {days}d {hours}h"
                await update.message.reply_text(msg, parse_mode='Markdown')
                return
            
            msg = f"📬 *Inbox for:* `{email['address']}`\n"
            for i, message in enumerate(messages, 1):
                msg_id = message['id']
                content_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={login}&domain={domain}&id={msg_id}"
                content_response = requests.get(content_url)
                
                if content_response.status_code == 200:
                    content = content_response.json()
                    msg += f"\n📧 *Message {i}:*"
                    msg += f"\nFrom: `{content.get('from', 'Unknown')}`"
                    msg += f"\nSubject: {content.get('subject', 'No subject')}"
                    msg += f"\nDate: {content.get('date', 'Unknown')}"
                    if content.get('textBody'):
                        body = content['textBody'].replace('\r', '').replace('\n', ' ')[:200]
                        msg += f"\nBody: {body}..."
                    msg += "\n"
            
            remaining = email['expires'] - now
            days = remaining.days
            hours = int(remaining.seconds / 3600)
            msg += f"\n⏱ Email expires in: {days}d {hours}h"
            
            await update.message.reply_text(msg, parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ Error checking messages. Please try again.")
            
    except Exception as e:
        print(f"Debug error: {str(e)}")
        await update.message.reply_text("❌ Error checking messages. Please try again.")

async def check_time(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("📭 No emails yet. Use /gen to create one.")
        return
    
    now = datetime.now()
    active_emails = [e for e in context.user_data['emails'] if e['expires'] > now]
    
    if not active_emails:
        await update.message.reply_text("📭 All emails expired. Use /gen to create new one.")
        return
    
    msg = "⏱ *Email Expiration Times:*\n"
    for i, email in enumerate(active_emails, 1):
        remaining = email['expires'] - now
        days = remaining.days
        hours = int(remaining.seconds / 3600)
        msg += f"\n{i}. `{email['address']}`"
        msg += f"\nExpires in: {days}d {hours}h\n"
    
    await update.message.reply_text(msg, parse_mode='Markdown')

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("cmds", cmds))
    app.add_handler(CommandHandler("gen", generate_email))
    app.add_handler(CommandHandler("list", list_emails))
    app.add_handler(CommandHandler("check", check_messages))
    app.add_handler(CommandHandler("time", check_time))
    
    print("Bot starting...")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url="https://temp-mail-bot-j4bi.onrender.com"
    )

if __name__ == "__main__":
    main()
