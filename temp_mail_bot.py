from telegram.ext import Application, CommandHandler
import random
import os
from datetime import datetime, timedelta
import aiohttp
import asyncio

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

async def start(update, context):
    await update.message.reply_text("Commands:\n/gen1 - Generate 1secmail\n/gen2 - Generate temp-mail\n/check - Check messages\n/list - Show emails")

async def get_email():
    async with aiohttp.ClientSession() as session:
        async with session.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1") as response:
            data = await response.json()
            return data[0]

async def gen_1secmail(update, context):
    try:
        email = await get_email()
        
        if "emails" not in context.user_data:
            context.user_data["emails"] = []
            
        email_data = {
            "address": email,
            "service": "1secmail",
            "created": datetime.now(),
            "login": email.split("@")[0],
            "domain": email.split("@")[1]
        }
        
        context.user_data["emails"].append(email_data)
        await update.message.reply_text("New email created: " + email)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        await update.message.reply_text("Error generating email. Please try again.")

async def gen_tempmail(update, context):
    try:
        email = await get_email()
        
        if "emails" not in context.user_data:
            context.user_data["emails"] = []
            
        email_data = {
            "address": email,
            "service": "tempmail",
            "created": datetime.now(),
            "login": email.split("@")[0],
            "domain": email.split("@")[1]
        }
        
        context.user_data["emails"].append(email_data)
        await update.message.reply_text("New email created: " + email)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        await update.message.reply_text("Error generating email. Please try again.")

async def list_mail(update, context):
    if "emails" not in context.user_data or not context.user_data["emails"]:
        await update.message.reply_text("No active emails")
        return
        
    msg = "Your emails:\n\n"
    for idx, email in enumerate(context.user_data["emails"], 1):
        msg += str(idx) + ". " + email["address"] + "\n"
        msg += "Service: " + email["service"] + "\n"
        msg += "Created: " + email["created"].strftime("%H:%M:%S") + "\n\n"
    
    await update.message.reply_text(msg)

async def check_messages(update, context):
    if "emails" not in context.user_data or not context.user_data["emails"]:
        await update.message.reply_text("Generate an email first using /gen1 or /gen2")
        return
        
    email = context.user_data["emails"][-1]
    
    try:
        async with aiohttp.ClientSession() as session:
            if email["service"] == "1secmail":
                url = f"https://www.1secmail.com/api/v1/?action=getMessages&login={email['login']}&domain={email['domain']}"
                async with session.get(url) as response:
                    messages = await response.json()
                
                if not messages:
                    await update.message.reply_text(f"No messages for {email['address']}")
                    return
                    
                msg = f"Inbox for {email['address']}:\n\n"
                for idx, message in enumerate(messages, 1):
                    msg_id = message["id"]
                    msg_url = f"https://www.1secmail.com/api/v1/?action=readMessage&login={email['login']}&domain={email['domain']}&id={msg_id}"
                    async with session.get(msg_url) as msg_response:
                        msg_content = await msg_response.json()
                    
                    msg += f"Message #{idx}\n"
                    msg += f"From: {message['from']}\n"
                    msg += f"Subject: {message['subject']}\n"
                    msg += f"Date: {message['date']}\n"
                    if "textBody" in msg_content:
                        msg += f"Body: {msg_content['textBody'][:200]}...\n\n"
                        
            else:
                await update.message.reply_text("Using 1secmail service")
                return
                
            await update.message.reply_text(msg)
            
    except Exception as e:
        print(f"Error: {str(e)}")
        await update.message.reply_text("Error checking messages. Please try again.")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen1", gen_1secmail))
    app.add_handler(CommandHandler("gen2", gen_tempmail))
    app.add_handler(CommandHandler("list", list_mail))
    app.add_handler(CommandHandler("check", check_messages))
    
    print("Starting bot...")
    app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url="https://temp-mail-bot-j4bi.onrender.com")

if __name__ == "__main__":
    main()
