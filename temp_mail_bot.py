from telegram.ext import Application, CommandHandler
import random
import string
import re
from datetime import datetime, timedelta
import os

# Get port from environment
PORT = int(os.getenv("PORT", 8080))
TOKEN = os.getenv("TOKEN", 
"7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0")

# ... rest of your code ...

def main():
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', start_command))
    app.add_handler(CommandHandler('generate', generate_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('list', list_command))
    app.add_handler(CommandHandler('check', check_messages))
    app.add_handler(CommandHandler('delete', delete_command))
    app.add_handler(CommandHandler('domains', domains_command))
    
    print("✨ Bot is starting...")
    # Add webhook mode
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url="https://your-app-name.onrender.com"
    )

if __name__ == '__main__':
    main()

