from telegram.ext import Application, CommandHandler
import random
import os
from datetime import datetime, timedelta

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"
PORT = int(os.getenv("PORT", "8080"))

async def start(update, context):
    await update.message.reply_text("Commands: /gen /list /time /check")

async def gen(update, context):
    num = random.randint(1000,9999)
    email = "user" + str(num) + "@tempmail.com"
    if "emails" not in context.user_data:
        context.user_data["emails"] = []
    email_data = {"address": email, "expires": datetime.now() + timedelta(minutes=10), "messages": []}
    context.user_data["emails"].append(email_data)
    await update.message.reply_text("New email: " + email)

async def list_mail(update, context):
    if "emails" not in context.user_data:
        await update.message.reply_text("No emails")
        return
    now = datetime.now()
    active = []
    for e in context.user_data["emails"]:
        if e["expires"] > now:
            active.append(e)
    if not active:
        await update.message.reply_text("No active emails")
        return
    msg = "Your emails:"
    for i in range(len(active)):
        msg = msg + "
" + str(i+1) + ". " + active[i]["address"]
    await update.message.reply_text(msg)

async def time_command(update, context):
    if "emails" not in context.user_data:
        await update.message.reply_text("No emails")
        return
    now = datetime.now()
    active = []
    for e in context.user_data["emails"]:
        if e["expires"] > now:
            active.append(e)
    if not active:
        await update.message.reply_text("All expired")
        return
    email = active[-1]
    remaining = email["expires"] - now
    minutes = int(remaining.total_seconds() / 60)
    await update.message.reply_text("Minutes left: " + str(minutes))

async def check_messages(update, context):
    if "emails" not in context.user_data:
        await update.message.reply_text("No emails")
        return
    now = datetime.now()
    active = []
    for e in context.user_data["emails"]:
        if e["expires"] > now:
            active.append(e)
    if not active:
        await update.message.reply_text("All expired")
        return
    email = active[-1]
    if random.random() < 0.3:
        num = random.randint(1000,9999)
        msg = {"from": "user" + str(num) + "@example.com", "time": datetime.now().strftime("%H:%M:%S")}
        email["messages"].append(msg)
    if not email["messages"]:
        await update.message.reply_text("No messages")
    else:
        txt = "Messages:"
        for i in range(len(email["messages"])):
            txt = txt + "
" + str(i+1) + ". From: " + email["messages"][i]["from"]
        await update.message.reply_text(txt)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("list", list_mail))
    app.add_handler(CommandHandler("time", time_command))
    app.add_handler(CommandHandler("check", check_messages))
    print("Starting...")
    app.run_webhook(listen="0.0.0.0", port=PORT, webhook_url="https://temp-mail-bot-j4bi.onrender.com")

if __name__ == "__main__":
    main()
