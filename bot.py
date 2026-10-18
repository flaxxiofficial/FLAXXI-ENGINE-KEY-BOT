import telebot
import random
import string
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Token
TOKEN = "8868351923:AAHK25ihjj6D40xnzpHm16OHuFonQJnUhzI"
bot = telebot.TeleBot(TOKEN)

# Owner ID & Firebase URL
OWNER_ID = 6903735098
FIREBASE_URL = "https://flaxxi-23171-default-rtdb.firebaseio.com"

# Random Key Generator Function (AimAi hata diya gaya hai)
def generate_key(prefix="FLAXXI"):
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-{suffix}"

# --- /start COMMAND (Deep Link Handler) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    
    # Jab user ad complete karke wapas aayega
    if len(args) > 1 and args[1] == "verify_claimkey":
        key = generate_key()
        
        # Firebase Database mein key save karein
        data = {"key": key, "status": "ACTIVE"}
        try:
            requests.post(f"{FIREBASE_URL}/keys.json", json=data)
        except Exception as e:
            print("Firebase Error:", e)
        
        bot.send_message(
            message.chat.id,
            f"🎉 **Verification Successful!**\n\n"
            f"🔑 **Your Key:**\n`{key}`\n\n"
            f"⏳ **Validity:** 24 Hours\n"
            f"⚡ **FLAXXI ENGINE**",
            parse_mode="Markdown"
        )
        return

    # Normal /start message with Ad link
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    
    ad_short_link = "https://srnky.com/EGLiVw1ME"
    
    markup.add(
        InlineKeyboardButton("Verify ✅", url=ad_short_link)
    )
    
    welcome_text = (
        "🛡️ **Human Verification Required**\n\n"
        "Please watch the sponsored ad below to verify and get your key."
    )
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup, parse_mode="Markdown")

# --- /owner COMMAND (ADMIN PANEL) ---
@bot.message_handler(commands=['owner'])
def owner_panel(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ **You are not authorized.**", parse_mode="Markdown")
        return

    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("➕ Add / Create Key", callback_data="admin_add_key"),
        InlineKeyboardButton("📋 View All Keys", callback_data="admin_view_keys")
    )
    
    bot.send_message(
        message.chat.id,
        "👑 **FLAXXI ENGINE - DPAdmin Panel**\n\nChoose an option:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# --- CALLBACK QUERY HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "admin_add_key":
        if call.from_user.id != OWNER_ID:
            return
        new_key = generate_key(prefix="FLAXXI-VIP")
        
        # Firebase mein VIP key save karein
        data = {"key": new_key, "status": "ACTIVE"}
        try:
            requests.post(f"{FIREBASE_URL}/keys.json", json=data)
        except Exception as e:
            print("Firebase Error:", e)
            
        bot.send_message(
            call.message.chat.id,
            f"✅ **VIP Key Created & Saved to Firebase!**\n\n🔑 `{new_key}`",
            parse_mode="Markdown"
        )
        
    elif call.data == "admin_view_keys":
        if call.from_user.id != OWNER_ID:
            return
        try:
            response = requests.get(f"{FIREBASE_URL}/keys.json")
            keys_data = response.json()
            if not keys_data:
                bot.send_message(call.message.chat.id, "📋 **No keys found in Firebase.**", parse_mode="Markdown")
            else:
                msg = "📋 **Firebase Active Keys:**\n\n"
                for k_id, item in keys_data.items():
                    if isinstance(item, dict):
                        msg += f"• `{item.get('key')}`\n"
                bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Error fetching keys: {e}")

# Bot ko run rakhne ke liye
bot.infinity_polling()
