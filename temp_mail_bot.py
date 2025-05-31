from telegram.ext import Application, CommandHandler
import random
import os
from datetime import datetime, timedelta
import requests
import json

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

async def start(update, context):
    await update.message.reply_text(
        "📧 TempMail Bot\n\n"
        "/gen1 - Generate 1secmail\n"
        "/gen2 - Generate temp-mail\n"
        "/check - Check messages\n"
        "/list - Show active emails"
    )

async def gen_1secmail(update, context):
    try:
        response = requests.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1')
        email = response.json()[0]
        
        if 'emails' not in context.user_data:
            context.user_data['emails'] = []
            
        email_data = {
            'address': email,
            'service': '1secmail',
            'created': datetime.now(),
            'login': email.split('@')[0],
            'domain': email.split('@')[1]
        }
        
        context.user_data['emails'].append(email_data)
        await update.message.reply_text(f"✨ New 1secmail email:\n📧 {email}")
        
    except Exception as e:
        await update.message.reply_text(f"Error generating email: {str(e)}")

async def gen_tempmail(update, context):
    try:
        # Using 1secmail as backup since temp-mail.org requires API key
        response = requests.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1')
        email = response.json()[0]
        
        if 'emails' not in context.user_data:
            context.user_data['emails'] = []
            
        email_data = {
            'address': email,
            'service': 'tempmail',
            'created': datetime.now(),
            'login': email.split('@')[0],
            'domain': email.split('@')[1]
        }
        
        context.user_data['emails'].append(email_data)
        await update.message.reply_text(f"✨ New temp-mail email:\n📧 {email}")
        
    except Exception as e:
        await update.message.reply_text(f"Error generating email: {str(e)}")

async def list_mail(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("📭 No active emails")
        return
        
    msg = "📧 Your active emails:\n\n"
    for idx, email in enumerate(context.user_data['emails'], 1):
        msg += f"{idx}. {email['address']}\n"
        msg += f"   Service: {email['service']}\n"
        msg += f"   Created: {email['created'].strftime('%H:%M:%S')}\n\n"
    
    await update.message.reply_text(msg)

async def check_messages(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("📭 Generate an email first using /gen1 or /gen2")
        return
        
    email = context.user_data['emails'][-1]
    
    try:
        if email['service'] == '1secmail':
            # Check 1secmail messages
            url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={email['login']}&domain={email['domain']}"
            response = requests.get(url)
            messages = response.json()
            
            if not messages:
                await update.message.reply_text(f"📭 No messages for {email['address']}")
                return
                
            msg = f"📬 Inbox for {email['address']}:\n\n"
            for idx, message in enumerate(messages, 1):
                # Get message content
                msg_id = message['id']
                msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={email['login']}&domain={email['domain']}&id={msg_id}"
                msg_response = requests.get(msg_url)
                msg_content = msg_response.json()
                
                msg += f"📧 Message #{idx}\n"
                msg += f"From: {message['from']}\n"
                msg += f"Subject: {message['subject']}\n"
                msg += f"Date: {message['date']}\n"
                if msg_content.get('textBody'):
                    msg += f"Body: {msg_content['textBody'][:200]}...\n\n"
                    
        else:
            # Temp-mail.org would go here if we had API key
            await update.message.reply_text("Using 1secmail service for now")
            return
            
        await update.message.reply_text(msg)
        
    except Exception as e:
        await update.message.reply_text(f"Error checking messages: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen1", gen_1secmail))
    app.add_handler(CommandHandler("gen2", gen_tempmail))
    app.add_handler(CommandHandler("list", list_mail))
    app.add_handler(CommandHandler("check", check_messages))
    
    print("✨ Bot is starting...")
    app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url="https://temp-mail-bot-j4bi.onrender.com")

if __name__ == "__main__":
    main()
