from telegram.ext import Application, CommandHandler
import random
import os
from datetime import datetime, timedelta

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

DOMAINS = ["tempmail.com", "throwaway.com", "quickmail.org"]
EXPIRATION_MINUTES = 10

async def start(update, context):
    await update.message.reply_text("Commands:\n/gen - New email\n/list - 
Show emails\n/time - Check time\n/check - Check messages")

async def gen(update, context):
    email = f"user{random.randint(1000,9999)}@{random.choice(DOMAINS)}"
    if "emails" not in context.user_data:
        context.user_data["emails"] = []
    
    email_data = {
        "address": email,
        "expires": datetime.now() + timedelta(minutes=EXPIRATION_MINUTES),
        "messages": []
    }
    context.user_data["emails"].append(email_data)
    await update.message.reply_text(f"New email: {email}\nExpires in: 
{EXPIRATION_MINUTES} minutes")

async def list_mail(update, context):
    if "emails" not in context.user_data:
        await update.message.reply_text("No emails")
        return
    
    now = datetime.now()
    active_emails = [e for e in context.user_data["emails"] if 
e["expires"] > now]
    
    if not active_emails:
        await update.message.reply_text("No active emails")
        return
    
    msg = "Your emails:\n\n"
    for i, email in enumerate(active_emails, 1):
        remaining = email["expires"] - now
        minutes = int(remaining.total_seconds() / 60)
        msg += f"{i}. {email['address']}\n"
        msg += f"   Time left: {minutes} minutes\n\n"
    
    await update.message.reply_text(msg)

async def time_command(update, context):
    if "emails" not in context.user_data:
        await update.message.reply_text("No emails")
        return
    
    now = datetime.now()
    active_emails = [e for e in context.user_data["emails"] if 
e["expires"] > now]
    
    if not active_emails:
        await update.message.reply_text("All emails expired")
        return
    
    email = active_emails[-1]
    remaining = email["expires"] - now
    minutes = int(remaining.total_seconds() / 60)
    await update.message.reply_text(f"Latest email: 
{email['address']}\nTime left: {minutes} minutes")

async def check_messages(update, context):
    if "emails" not in context.user_data:
        await update.message.reply_text("No emails")
        return
    
    now = datetime.now()
    active_emails = [e for e in context.user_data["emails"] if 
e["expires"] > now]
    
    if not active_emails:
        await update.message.reply_text("All emails expired")
        return
    
    email = active_emails[-1]
    
    # Simulate receiving a message
    if random.random() < 0.3:  # 30% chance of new message
        new_message = {
            "from": f"user{random.randint(1000,9999)}@example.com",
            "subject": f"Test message {len(email['messages']) + 1}",
            "time": datetime.now().strftime("%H:%M:%S")
        }
        email["messages"].append(new_message)
    
    if not email["messages"]:
        await update.message.reply_text(f"No messages for 
{email['address']}")
    else:
        msg = f"Messages for {email['address']}:\n\n"
        for i, message in enumerate(email["messages"], 1):
            msg += f"{i}. From: {message['from']}\n"
            msg += f"   Subject: {message['subject']}\n"
            msg += f"   Time: {message['time']}\n\n"
        await update.message.reply_text(msg)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("list", list_mail))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("check", check_messages))
    print("Starting...")
    app.run_webhook(listen="0.0.0.0", port=PORT, 
webhook_url="https://temp-mail-bot-j4bi.onrender.com")

if __name__ == "__main__":
    main()

