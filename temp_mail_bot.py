from telegram.ext import Application, CommandHandler
import random
import os
import aiohttp
from datetime import datetime

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

async def start(update, context):
    await update.message.reply_text("Commands:\n/gen - Generate new email\n/check - Check messages\n/list - Show emails")

async def generate_email(update, context):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1') as response:
                if response.status == 200:
                    data = await response.json()
                    email = data[0]
                    
                    if 'emails' not in context.user_data:
                        context.user_data['emails'] = []
                    
                    email_data = {
                        'address': email,
                        'login': email.split('@')[0],
                        'domain': email.split('@')[1],
                        'created': datetime.now()
                    }
                    
                    context.user_data['emails'].append(email_data)
                    await update.message.reply_text(f"📧 New email created:\n\n{email}\n\nUse /check to see messages")
                else:
                    await update.message.reply_text("Failed to generate email. Try again.")
    except Exception as e:
        print(f"Debug - Error: {str(e)}")
        await update.message.reply_text("Service temporarily unavailable. Try again in a few moments.")

async def list_emails(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("No emails yet. Use /gen to create one.")
        return
    
    msg = "Your emails:\n\n"
    for i, email in enumerate(context.user_data['emails'], 1):
        msg += f"{i}. {email['address']}\n"
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
            url = f'https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}'
            async with session.get(url) as response:
                if response.status == 200:
                    messages = await response.json()
                    
                    if not messages:
                        await update.message.reply_text(f"No messages for {email['address']}")
                        return
                    
                    msg = f"📬 Inbox for {email['address']}:\n\n"
                    for i, message in enumerate(messages, 1):
                        msg += f"📧 Message {i}:\n"
                        msg += f"From: {message.get('from', 'Unknown')}\n"
                        msg += f"Subject: {message.get('subject', 'No subject')}\n"
                        msg += f"Date: {message.get('date', 'Unknown')}\n\n"
                    
                    await update.message.reply_text(msg)
                else:
                    await update.message.reply_text("Failed to fetch messages. Try again.")
    except Exception as e:
        print(f"Debug - Error: {str(e)}")
        await update.message.reply_text("Error checking messages. Try again in a few moments.")

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
