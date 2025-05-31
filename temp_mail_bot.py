from telegram.ext import Application, CommandHandler
import random
import os
from datetime import datetime, timedelta

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

DOMAINS = ["tempmail.com", "throwaway.com", "quickmail.org"]
EXPIRATION_MINUTES = 10

async def start(update, context):
    await update.message.reply_text("Commands: /gen /list /time /check")

async def gen(update, context):
    email = "user" + str(random.randint(1000,9999)) + "@" + 
random.choice(DOMAINS)
    if "emails" not in context.user_data:
        context.user_data["emails"] = []
    email_data = {"address": email, "expires": datetime.now() + 
timedelta(minutes=EXPIRATION_MINUTES), "messages": []}
    context.user_data["emails"].append(email_data)
    await update.message.reply_text("New email: " + email)

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
    msg = "Your emails:"
    for i, email in enumerate(active_emails, 1):
        remaining = email["expires"] - now
        minutes = int(remaining.total_seconds() / 60)
        msg += "\n" + str(i) + ". " + email["address"] + " (" + 
str(minutes) + "m)"
    await update.message.reply_text(msg)

async def time_command(update, context):
    if "emails" not in context.user_data:
        await update.message.reply_text("No emails")
        return
    now = datetime.now()
    active_emails = [e for e in context.user_data["emails"] if 
e["expires"] > now]
    if not active_emails:
        await update.message.reply_text("All expired")
        return
    email = active_emails[-1]
    remaining = email["expires"] - now
    minutes = int(remaining.total_seconds() / 60)
    await update.message.reply_text("Time left: " + str(minutes) + "m")

async def check_messages(update, context):
    if "emails" not in context.user_data:
        await update.message.reply_text("No emails")
        return
    now = datetime.now()
    active_emails = [e for e in context.user_data["emails"] if 
e["expires"] > now]
    if not active_emails:
        await update.message.reply_text("All expired")
        return
    email = active_emails[-1]
    if random.random() < 0.3:
        new_message = {
            "from": "user" + str(random.randint(1000,9999)) + 
"@example.com",
            "time": datetime.now().strftime("%H:%M:%S")
        }
        email["messages"].append(new_message)
    if not email["messages"]:
        await update.message.reply_text("No messages")
    else:
        msg = "Messages:"
        for i, message in enumerate(email["messages"], 1):
            msg += "\n" + str(i) + ". From: " + message["from"] + " Time: 
" + message["time"]
        await update.message.reply_text(msg)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("list", list_mail))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("check", check_messages))
    print("Bot starting...")
    app.run_webhook(listen="0.0.0.0", port=PORT, 
webhook_url="https://temp-mail-bot-j4bi.onrender.com")

if __name__ == "__main__":
    main()

