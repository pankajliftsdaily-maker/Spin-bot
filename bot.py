import random
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- FLASK WEB SERVER SETUP ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# --- TELEGRAM BOT LOGIC ---
# Yahan apni Telegram User ID daalein (Bina quotes ke)
OWNER_ID = 1869599187

# Security Check Function: Sirf Admin ya Owner ko allow karne ke liye
async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat_id = update.message.chat_id
    user_id = update.message.from_user.id
    
    if update.message.chat.type in ['group', 'supergroup']:
        user_member = await context.bot.get_chat_member(chat_id, user_id)
        is_group_admin = user_member.status in ['administrator', 'creator']
        return is_group_admin or user_id == OWNER_ID
    else:
        return user_id == OWNER_ID

# [/spin] Command: Isse fully random koi bhi video/gif chalega (Even aur Odd dono)
async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return

    chat_id = update.message.chat_id
    try:
        all_files = os.listdir('.')
        valid_extensions = ('.mp4', '.gif')
        video_list = [f for f in all_files if f.lower().endswith(valid_extensions)]

        if not video_list:
            print("Error: Folder mein koi file nahi mili!")
            return

        selected_file = random.choice(video_list)
        await context.bot.send_animation(chat_id=chat_id, animation=open(selected_file, 'rb'))
        print(f"Fully Randomly sent: {selected_file}")
    except Exception as e:
        print(f"File bhejte waqt error aayi: {e}")

# [/77] Command: Isse SIRF ODD number wali files (1, 3, 5, 7, 9) hi chalengi
async def spin_odd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_authorized(update, context):
        return

    chat_id = update.message.chat_id
    try:
        all_files = os.listdir('.')
        valid_extensions = ('.mp4', '.gif')
        
        odd_files = []
        for f in all_files:
            if f.lower().endswith(valid_extensions):
                # File ka naam bina extension ke nikalna (jaise '3.mp4' se sirf '3' alag karna)
                name_part = os.path.splitext(f)[0]
                
                # Check karna ki kya file ka naam ek number hai aur wo ODD hai
                if name_part.isdigit() and int(name_part) % 2 != 0:
                    odd_files.append(f)

        # Agar folder mein koi bhi odd number wali file nahi milti
        if not odd_files:
            print("Error: Folder mein koi bhi ODD number (1,3,5,7,9) wali file nahi mili!")
            return

        # Sirf odd number wali files mein se randomly ek chunnna
        selected_file = random.choice(odd_files)
        await context.bot.send_animation(chat_id=chat_id, animation=open(selected_file, 'rb'))
        print(f"Odd mode mein randomly bheja: {selected_file}")
    except Exception as e:
        print(f"Odd file bhejte waqt error aayi: {e}")

# Auto-Leave Feature: Agar owner admin nahi hai toh group chhod dena
async def check_bot_added(update: Update, context: ContextTypes.DEFAULT_TYPE):
    new_members = update.message.new_chat_members
    chat_id = update.message.chat_id
    bot_id = context.bot.id

    for member in new_members:
        if member.id == bot_id:
            try:
                owner_member = await context.bot.get_chat_member(chat_id, OWNER_ID)
                if owner_member.status not in ['administrator', 'creator']:
                    await context.bot.leave_chat(chat_id)
            except Exception:
                await context.bot.leave_chat(chat_id)
            break

def main():
    # Yahan apna Bot Token daalein jo BotFather se mila tha
    TOKEN = "8879402310:AAH_KKAhPnIAwfq4f3dvXtqiOoSikxq81J8"

    application = Application.builder().token(TOKEN).build()
    
    # Dono commands ko register karna
    application.add_handler(CommandHandler("spin", spin))
    application.add_handler(CommandHandler("77", spin_odd))
    
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, check_bot_added))

    # Background mein web server chalana 24/7 online rakhne ke liye
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("Bot is ready with /spin and /77 commands!")
    application.run_polling()

if __name__ == '__main__':
    main()
