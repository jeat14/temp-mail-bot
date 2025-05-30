from telegram.ext import Application, CommandHandler
import random
import string
import re
from datetime import datetime, timedelta

TOKEN = "7744035483:AAFYnyfwhN74kSveZBl7nXKjGgXKYWtnbw0"

DOMAINS = ['tempmail.com', 'temp-mail.org', 'throwawaymail.com', 'temp.mail']

async def start_command(update, context):
    help_text = "📧 TempMail Bot\n\n"
    help_text += "🔹 /generate - New random email\n"
    help_text += "🔹 /custom prefix - Custom email\n"
    help_text += "🔹 /list - Show active emails\n"
    help_text += "🔹 /check - Check messages\n"
    help_text += "🔹 /delete - Delete last email\n"
    help_text += "🔹 /domains - List available domains"
    await update.message.reply_text(help_text)

def generate_random_string(length=10):
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def is_valid_prefix(prefix):
    return bool(re.match("^[a-zA-Z0-9_-]+$", prefix))

async def generate_command(update, context):
    random_name = generate_random_string()
    domain = random.choice(DOMAINS)
    email = f"{random_name}@{domain}"
    
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
        
    email_data = {
        'address': email,
        'created': datetime.now(),
        'messages': [],
        'expires': datetime.now() + timedelta(hours=24)
    }
    
    context.user_data['emails'].append(email_data)
    
    response = "✨ New email created!\n\n"
    response += f"📧 {email}\n"
    response += f"⏱ Expires in 24 hours\n"
    response += f"📥 Use /check to see messages"
    
    await update.message.reply_text(response)

async def custom_command(update, context):
    if not context.args:
        await update.message.reply_text("❌ Usage: /custom yourprefix\nExample: /custom john123")
        return
        
    prefix = context.args[0].lower()
    if not is_valid_prefix(prefix):
        await update.message.reply_text("❌ Prefix can only contain letters, numbers, underscore and dash")
        return
        
    if len(prefix) < 3:
        await update.message.reply_text("❌ Prefix must be at least 3 characters long")
        return
        
    domain = random.choice(DOMAINS)
    email = f"{prefix}{generate_random_string(5)}@{domain}"
    
    if 'emails' not in context.user_data:
        context.user_data['emails'] = []
        
    email_data = {
        'address': email,
        'created': datetime.now(),
        'messages': [],
        'expires': datetime.now() + timedelta(hours=24)
    }
    
    context.user_data['emails'].append(email_data)
    
    response = "✨ Custom email created!\n\n"
    response += f"📧 {email}\n"
    response += f"⏱ Expires in 24 hours\n"
    response += f"📥 Use /check to see messages"
    
    await update.message.reply_text(response)

async def list_command(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("📭 You have no active emails")
        return
        
    now = datetime.now()
    active_emails = []
    
    for email in context.user_data['emails']:
        if email['expires'] > now:
            active_emails.append(email)
            
    if not active_emails:
        await update.message.reply_text("📭 You have no active emails")
        return
        
    response = "📧 Your active emails:\n\n"
    
    for idx, email in enumerate(active_emails, 1):
        time_left = email['expires'] - now
        hours_left = int(time_left.total_seconds() / 3600)
        response += f"{idx}. {email['address']}\n"
        response += f"   ⏱ Expires in {hours_left} hours\n"
        response += f"   📥 Messages: {len(email['messages'])}\n\n"
    
    await update.message.reply_text(response)

async def check_messages(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("📭 Generate an email first using /generate")
        return
        
    now = datetime.now()
    active_emails = [e for e in context.user_data['emails'] if e['expires'] > now]
    
    if not active_emails:
        await update.message.reply_text("📭 You have no active emails")
        return
        
    email = active_emails[-1]
    
    # Simulate receiving a new message
    if random.random() < 0.3:  # 30% chance of new message
        new_message = {
            'from': f"user{random.randint(1000,9999)}@example.com",
            'subject': f"Test message {len(email['messages']) + 1}",
            'time': datetime.now()
        }
        email['messages'].append(new_message)
    
    if not email['messages']:
        await update.message.reply_text(f"📭 No messages for {email['address']}")
        return
        
    response = f"📧 Messages for {email['address']}:\n\n"
    
    for idx, msg in enumerate(email['messages'], 1):
        response += f"{idx}. From: {msg['from']}\n"
        response += f"   Subject: {msg['subject']}\n"
        response += f"   Time: {msg['time'].strftime('%H:%M:%S')}\n\n"
    
    await update.message.reply_text(response)

async def domains_command(update, context):
    response = "🌐 Available domains:\n\n"
    for domain in DOMAINS:
        response += f"• {domain}\n"
    await update.message.reply_text(response)

async def delete_command(update, context):
    if 'emails' not in context.user_data or not context.user_data['emails']:
        await update.message.reply_text("📭 No emails to delete")
        return
        
    deleted = context.user_data['emails'].pop()
    await update.message.reply_text(f"🗑 Deleted: {deleted['address']}")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', start_command))
    app.add_handler(CommandHandler('generate', generate_command))
    app.add_handler(CommandHandler('custom', custom_command))
    app.add_handler(CommandHandler('list', list_command))
    app.add_handler(CommandHandler('check', check_messages))
    app.add_handler(CommandHandler('delete', delete_command))
    app.add_handler(CommandHandler('domains', domains_command))
    
    print("✨ Bot is starting...")
    app.run_polling(poll_interval=1.0)

if __name__ == '__main__':
    main()
