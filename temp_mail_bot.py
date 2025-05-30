from telegram.ext import Application, CommandHandler
import random
import string
import os

PORT = int(os.getenv("PORT", "8080"))
TOKEN = os.getenv("TOKEN", 
"7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0")

DOMAINS = ['tempmail.com', 'temp-mail.org', 'throwawaymail.com']

async def start_command(update, context):
    await update.message.reply_text("/generate - New email\n/custom - 
Custom email\n/list - Show emails\n/delete - Remove email")

def generate_random_string(length=10):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

async def generate_command(update, context):
    random_name = generate_random_string()
    domain = random.choice(DOMAINS)
    email = f"{random_name}@{domain}"
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
    context.user_data['emails'].append(email)
    await update.message.reply_text(f"New email: {email}")

async def custom_command(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /custom yourprefix")
        return
    prefix = context.args[0].lower()
    domain = random.choice(DOMAINS)
    email = f"{prefix}{generate_random_string(5)}@{domain}"
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
    context.user_data['emails'].append(email)
    await update.message.reply_text(f"Custom email: {email}")

async def list_command(update, context):
    if 'emails' not in context.user_data or not 
context.user_data['emails']:
        await update.message.reply_text("No emails")
        return
    message = "Your emails:"
    for idx, email in enumerate(context.user_data['emails'], 1):
        message += f"\n{idx}. {email}"
    await update.message.reply_text(message)

async def delete_command(update, context):
    if 'emails' not in context.user_data or not 
context.user_data['emails']:
        await update.message.reply_text("No emails")
        return
    deleted = context.user_data['emails'].pop()
    await update.message.reply_text(f"Deleted: {deleted}")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', start_command))
    app.add_handler(CommandHandler('generate', generate_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('list', list_command))
    app.add_handler(CommandHandler('delete', delete_command))

    print("Bot starting...")
    app.run_polling()

if __name__ == '__main__':
    main()

