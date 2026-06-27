import random
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- FLASK WEB SERVER SETUP ---
# Render ko dikhane ke liye ki bot active hai
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive 24/7!"

def run_flask():
    # Render port automatically assign karta hai, local ke liye default 5000
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT LOGIC ---
# Yahan apni Telegram User ID daalein 
OWNER_ID = 123456789  
# Aapke GIFs ke naam
GIF_LIST = ['1.gif', '3.gif', '5.gif', '7.gif', '9.gif']

# /spin command ka function
async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    
    # Check karna ki message kisi Group se aaya hai ya Private chat se
    if update.message.chat.type in ['group', 'supergroup']:
        user_member = await context.bot.get_chat_member(chat_id, user_id)
        is_group_admin = user_member.status in ['administrator', 'creator']
        
        # Agar command dene wala Admin nahi hai aur Owner bhi nahi hai, toh ignore kar do
        if not is_group_admin and user_id != OWNER_ID:
            print(f"Ignored /spin from non-admin user: {user_id}")
            return
    else:
        # Private chat me sirf Owner use kar sakta hai
        if user_id != OWNER_ID:
            return

    # Random GIF select karke bhejna
    selected_gif = random.choice(GIF_LIST)
    try:
        await context.bot.send_animation(chat_id=chat_id, animation=open(selected_gif, 'rb'))
        print(f"GIF sent: {selected_gif}")
    except Exception as e:
        print(f"GIF bhejte waqt error aayi: {e}")

# Auto-Leave Feature: Jab bot group me add ho
async def check_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_members = update.message.new_chat_members
    chat_id = update.message.chat_id
    bot_id = context.bot.id

    for member in new_members:
        if member.id == bot_id:
            print("Bot naye group me add hua. Owner status check ho raha hai...")
            try:
                owner_member = await context.bot.get_chat_member(chat_id, OWNER_ID)
                # Agar Owner group me admin nahi hai, toh bot leave kar dega
                if owner_member.status not in ['administrator', 'creator']:
                    print("Owner admin nahi hai. Bot group chhod raha hai...")
                    await context.bot.leave_chat(chat_id)
                else:
                    print("Owner admin hai. Bot group me rukega.")
            except Exception:
                # Agar owner group me hai hi nahi, tab bhi bot leave kar dega
                print("Owner group me nahi mila. Bot group chhod raha hai...")
                await context.bot.leave_chat(chat_id)
            break

def main():
    # Yahan apna Bot Token daalein
    TOKEN = "YAHAN_APNA_TOKEN_PASTE_KAREIN"

    # Telegram Application Setup
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("spin", spin))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, check_bot_added))

    # --- START FLASK SERVER IN A SEPARATE THREAD ---
    # Isse Flask server background me chalega aur Telegram bot block nahi hoga
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Start Telegram Bot
    print("Bot is ready, secure, and Flask server is running!")
    application.run_polling()

if __name__ == '__main__':
    main()
    
