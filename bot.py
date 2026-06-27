import random
import os
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- FLASK SERVER (24/7 Alive rakhne ke liye) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive, Secure and Global Mode System is Active!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, use_reloader=False)

# --- GLOBAL CONFIGURATION & CACHE ---
CURRENT_MODE = 'all'  # Default mode 'all' rahega (Globally controlled)
VIDEO_CACHE = []      # Super-fast speed ke liye memory cache

# DHYAN DEIN: Yahan 123456789 hata kar apni asli Telegram ID zaroor daalein!
OWNER_ID = 1869599187

# Speed Optimization: Files ko startup par hi load karna
def load_video_cache():
    global VIDEO_CACHE
    try:
        all_files = os.listdir('.')
        valid_extensions = ('.mp4', '.gif')
        VIDEO_CACHE = [f for f in all_files if f.lower().endswith(valid_extensions)]
        print(f"Fast Storage Active: {len(VIDEO_CACHE)} files loaded into memory.")
    except Exception as e:
        print(f"Cache load karne me error: {e}")

# Security Check Function
async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not update.message or not update.message.from_user:
        return False
        
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    
    if update.message.chat.type in ['group', 'supergroup']:
        try:
            # Rule 1: Kya BOT khud group me Admin hai?
            bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
            if bot_member.status != 'administrator':
                return False
                
            # Rule 2: Kya OWNER group me Admin hai?
            owner_member = await context.bot.get_chat_member(chat_id, OWNER_ID)
            if owner_member.status not in ['administrator', 'creator']:
                return False

            # Rule 3: Kya command dene wala member Admin/Owner hai?
            user_member = await context.bot.get_chat_member(chat_id, user_id)
            is_user_admin = user_member.status in ['administrator', 'creator']
            return is_user_admin or user_id == OWNER_ID
            
        except Exception as e:
            print(f"Rights check error: {e}")
            return False
    else:
        return user_id == OWNER_ID

# [/18] Command: Random Mode (Globally active, Local reply)
async def set_random_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE
    if not await is_authorized(update, context):
        return

    CURRENT_MODE = 'all'  # Global change
    print("Global Mode switched to: RANDOM")
    # update.message.reply_text sirf usi group me reply karega jahan command mili hai
    await update.message.reply_text("Random mode active")

# [/77] Command: Odd Mode (Globally active, Local reply)
async def set_odd_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE
    if not await is_authorized(update, context):
        return

    CURRENT_MODE = 'odd'  # Global change
    print("Global Mode switched to: ODD")
    await update.message.reply_text("Odd mode active")

# [/66] Command: Even Mode (Globally active, Local reply)
async def set_even_mode(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE
    if not await is_authorized(update, context):
        return

    CURRENT_MODE = 'even'  # Global change
    print("Global Mode switched to: EVEN")
    await update.message.reply_text("Even mode active")

# [/spin] Command: Precise 1:1 Instant Reply System
async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENT_MODE, VIDEO_CACHE
    if not await is_authorized(update, context):
        return

    if not VIDEO_CACHE:
        load_video_cache()

    if not VIDEO_CACHE:
        return

    try:
        final_filtered_list = []

        # 1. Odd Mode Filtering
        if CURRENT_MODE == 'odd':
            for f in VIDEO_CACHE:
                name_part = os.path.splitext(f)[0]
                if name_part.isdigit() and int(name_part) % 2 != 0:
                    final_filtered_list.append(f)
                    
        # 2. Even Mode Filtering
        elif CURRENT_MODE == 'even':
            for f in VIDEO_CACHE:
                name_part = os.path.splitext(f)[0]
                if name_part.isdigit() and int(name_part) % 2 == 0:
                    final_filtered_list.append(f)
                    
        # 3. Random Mode (Saari files)
        else:
            final_filtered_list = VIDEO_CACHE

        # Strict Single Execution: 1 command = exactly 1 reply animation sent once
        if final_filtered_list:
            selected_file = random.choice(final_filtered_list)
            await update.message.reply_animation(animation=open(selected_file, 'rb'))
            print(f"Processed 1 /spin command under mode [{CURRENT_MODE}] -> sent: {selected_file}")

    except Exception as e:
        print(f"Spin command error: {e}")

# Auto-Leave Rule: Agar Owner group chhod deta hai toh Bot bhi chhod dega
async def check_left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    left_member = update.message.left_chat_member
    chat_id = update.message.chat_id
    
    if left_member and left_member.id == OWNER_ID:
        try:
            await context.bot.leave_chat(chat_id)
            print("Owner left the group. Bot auto-left successfully.")
        except Exception as e:
            print(f"Auto-leave error: {e}")

def main():
    # Yahan apna Bot Token daalein
    TOKEN = "8879402310:AAH_KKAhPnIAwfq4f3dvXtqiOoSikxq81J8"

    # Memory me files cache load karna speed optimization ke liye
    load_video_cache()

    application = Application.builder().token(TOKEN).build()
    
    # Handlers register karna
    application.add_handler(CommandHandler("spin", spin))
    application.add_handler(CommandHandler("18", set_random_mode))
    application.add_handler(CommandHandler("77", set_odd_mode))
    application.add_handler(CommandHandler("66", set_even_mode))
    
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, check_left_member))

    # Background Flask Web Server
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("Strict 1:1 Response & Isolated Mode Notifications Bot is Ready!")
    # drop_pending_updates=True lagaya hai taaki startup par purane taps stack na ho aur fresh 1:1 chalu ho
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
