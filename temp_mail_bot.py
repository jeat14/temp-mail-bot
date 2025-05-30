from telegram.ext import Application, CommandHandler
import random
import string
import os

# Load environment variables
PORT = int(os.getenv("PORT", "8080"))
TOKEN = os.getenv("TOKEN", "your-telegram-bot-token")  # Replace with your 
actual token
APP_URL = os.getenv("APP_URL", "https://your-app-name.onrender.com")  # 
Replace with your Render URL

# Temp mail domains
DOMAINS = ['tempmail.com', 'temp-mail.org', 'throwawaymail.com']

# /start and /help handler
async def start_command(update, context):
    await update.message.reply_text(
        "Commands:\n"
        "/generate - Generate a random email\n"
        "/custom <prefix> - Create a custom email\n"
        "/list - List your generated emails\n"
        "/delete - Delete your last email"
    )

# Utility: generate random string
def generate_random_string(length=10):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

# /generate command
async def generate_command(update, context):
    random_name = generate_random_string()
    domain = random.choice(DOMAINS)
    email = f"{random_name}@{domain}"
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
    context.user_data['emails'].append(email)
    await update.message.reply_text(f"New email: {email}")

# /custom command
async def custom_command(update, context):
    if not context.args:
        await update.message.reply_text("Usage: /custom <yourprefix>")
        return
    prefix = context.args[0].lower()
    domain = random.choice(DOMAINS)
    email = f"{prefix}{generate_random_string(5)}@{domain}"
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
    context.user_data['emails'].append(email)
    await update.message.reply_text(f"Custom email: {email}")

# /list command
async def list_command(update, context):
    if 'emails' not in context.user_data or not 
context.user_data['emails']:
        await update.message.reply_text("No emails yet.")
        return
    message = "Your emails:"
    for idx, email in enumerate(context.user_data['emails'], 1):
        message += f"\n{idx}. {email}"
    await update.message.reply_text(message)

# /delete command
async def delete_command(update, context):
    if 'emails' not in context.user_data or not 
context.user_data['emails']:
        await update.message.reply_text("No emails to delete.")
        return
    deleted = context.user_data['emails'].pop()
    await update.message.reply_text(f"Deleted: {deleted}")

# Main bot setup
def main():
    app = Application.builder().token(TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', start_command))
    app.add_handler(CommandHandler('generate', generate_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('list', list_command))
    app.add_handler(CommandHandler('delete', delete_command))

    print("Bot starting...")

    # Start webhook for Render
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=f"{APP_URL}/{TOKEN}"
    )

if __name__ == '__main__':
    main()
