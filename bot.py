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
    return "Bot is Alive and Secure!"

def run_flask():
    port = int(os.environ.get("PORT", 5000))
    # use_reloader=False zaroori hai taaki background thread crash na ho
    app.run(host='0.0.0.0', port=port, use_reloader=False)

# --- BOT LOGIC ---
# DHYAN DEIN: Yahan 123456789 hata kar apni asli Telegram ID zaroor daalein!
OWNER_ID = 1869599187

# Security Check Function: Yeh function saare naye rules check karega
async def is_authorized(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.message.from_user.id
    chat_id = update.message.chat_id
    
    # Agar message group me aaya hai
    if update.message.chat.type in ['group', 'supergroup']:
        try:
            # Rule 1: Check karo ki kya BOT khud group me Admin hai?
            bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
            if bot_member.status != 'administrator':
                print("Bot admin nahi hai. Command ignore kar raha hoon.")
                return False
                
            # Rule 2: Check karo ki kya OWNER group me Admin (ya Creator) hai?
            owner_member = await context.bot.get_chat_member(chat_id, OWNER_ID)
            if owner_member.status not in ['administrator', 'creator']:
                print("Owner admin nahi hai. Command ignore kar raha hoon.")
                return False

            # Rule 3: Check karo ki command dene wala member Admin/Owner hai ya nahi?
            user_member = await context.bot.get_chat_member(chat_id, user_id)
            is_user_admin = user_member.status in ['administrator', 'creator']
            return is_user_admin or user_id == OWNER_ID
            
        except Exception as e:
            print(f"Rights check karte waqt error: {e}")
            return False
    else:
        # Private chat me sirf Owner bot chala sakta hai
        return user_id == OWNER_ID


# [/spin] Command Function
async def spin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Agar security check fail hua toh ignore (return)
    if not await is_authorized(update, context):
        return

    chat_id = update.message.chat_id
    try:
        all_files = os.listdir('.')
        valid_extensions = ('.mp4', '.gif')
        video_list = [f for f in all_files if f.lower().endswith(valid_extensions)]

        if video_list:
            selected_file = random.choice(video_list)
            await context.bot.send_animation(chat_id=chat_id, animation=open(selected_file, 'rb'))
    except Exception as e:
        print(f"Error: {e}")

# [/77] Command Function (Sirf Odd Numbers ke liye)
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
                name_part = os.path.splitext(f)[0]
                if name_part.isdigit() and int(name_part) % 2 != 0:
                    odd_files.append(f)

        if odd_files:
            selected_file = random.choice(odd_files)
            await context.bot.send_animation(chat_id=chat_id, animation=open(selected_file, 'rb'))
    except Exception as e:
        print(f"Error: {e}")

# Auto-Leave Rule: Agar Owner group chhod deta hai toh Bot bhi chhod dega
async def check_left_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    left_member = update.message.left_chat_member
    chat_id = update.message.chat_id
    
    # Agar jo insaan group leave kar raha hai wo Owner hai
    if left_member and left_member.id == OWNER_ID:
        print("Owner ne group chhod diya hai. Bot auto-leave kar raha hai...")
        try:
            await context.bot.leave_chat(chat_id)
        except Exception as e:
            print(f"Auto-leave error: {e}")

def main():
    # Yahan apna Bot Token daalein
    TOKEN = "8879402310:AAH_KKAhPnIAwfq4f3dvXtqiOoSikxq81J8"

    application = Application.builder().token(TOKEN).build()
    
    # Handlers add karna
    application.add_handler(CommandHandler("spin", spin))
    application.add_handler(CommandHandler("77", spin_odd))
    application.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, check_left_member))

    # Web server ko background me start karna
    flask_thread = Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    print("Bot is ready and fully strictly secured!")
    # drop_pending_updates=True se bot kabhi hang nahi hoga aur purane messages ignore kar dega jab wo on hoga
    application.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
