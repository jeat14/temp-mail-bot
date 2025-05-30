from telegram.ext import Application, CommandHandler
import random
import string
import os

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"

async def start(update, context):
    await update.message.reply_text("Commands: /gen /custom /list /del")

async def gen(update, context):
    email = f"user{random.randint(1000,9999)}@temp.mail"
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
    context.user_data['emails'].append(email)
    await update.message.reply_text(f"New: {email}")

async def custom(update, context):
    if not context.args:
        await update.message.reply_text("Use: /custom yourname")
        return
    prefix = context.args[0]
    email = f"{prefix}{random.randint(100,999)}@temp.mail"
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
    context.user_data['emails'].append(email)
    await update.message.reply_text(f"New: {email}")

async def list_mail(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("No emails")
        return
    msg = "Emails:"
    for i, email in enumerate(context.user_data['emails'], 1):
        msg += f"\n{i}. {email}"
    await update.message.reply_text(msg)

async def delete(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("No emails")
        return
    email = context.user_data['emails'].pop()
    await update.message.reply_text(f"Deleted: {email}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("gen", gen))
    app.add_handler(CommandHandler("custom", custom))
    app.add_handler(CommandHandler("list", list_mail))
    app.add_handler(CommandHandler("del", delete))
    print("Starting bot...")
    app.run_polling()

if __name__ == "__main__":
    main()
