from telegram.ext import Application, CommandHandler
import random
import string
import re
from datetime import datetime, timedelta
import os

# Get environment variables
PORT = int(os.getenv("PORT", "8080"))
TOKEN = os.getenv("TOKEN", 
"7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0")

DOMAINS = ['tempmail.com', 'temp-mail.org', 'throwawaymail.com']

# [Keep all your existing functions here]

def main():
    app = Application.builder().token(TOKEN).build()

    # Add handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', start_command))
    app.add_handler(CommandHandler('generate', generate_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('list', list_command))
    app.add_handler(CommandHandler('delete', delete_command))
    app.add_handler(CommandHandler('clear', clear_command))
    app.add_handler(CommandHandler('history', history_command))
    app.add_handler(CommandHandler('messages', check_messages))

    print("✨ Bot is starting...")
    
    # Use webhooks in production, polling in development
    if os.getenv("RENDER"):
        app.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{os.getenv('RENDER_EXTERNAL_URL', 
'example.com')}/{TOKEN}"
        )
    else:
        app.run_polling()

if __name__ == '__main__':
    main()

