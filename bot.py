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

# --- /start COMMAND (Deep Link Handler) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    
    # Jab user ad complete karke wapas aayega (deep link ke through)
    if len(args) > 1 and args[1] == "verify_claimkey":
        try:
            # Firebase se saari keys fetch karein (Timeout=10 to prevent freezing)
            response = requests.get(f"{FIREBASE_URL}/keys.json", timeout=10)
            keys_data = response.json()
            
            assigned_key = None
            key_firebase_id = None
            
            if keys_data:
                items = keys_data.items() if isinstance(keys_data, dict) else enumerate(keys_data)
                
                for k_id, item in items:
                    if isinstance(item, dict):
                        # Jo key active ho aur kisi ko na di gayi ho
                        if item.get("status") == "ACTIVE" and not item.get("claimed", False):
                            assigned_key = item.get("key")
                            key_firebase_id = k_id
                            break
            
            if assigned_key and key_firebase_id:
                # Us key ko Firebase mein 'claimed: True' mark karein
                requests.patch(
                    f"{FIREBASE_URL}/keys/{key_firebase_id}.json",
                    json={"claimed": True, "status": "USED"},
                    timeout=10
                )
                
                bot.send_message(
                    message.chat.id,
                    f"🎉 **Verification Successful!**\n\n"
                    f"🔑 **Your Key:**\n`{assigned_key}`\n\n"
                    f"⏳ **Validity:** 24 Hours\n"
                    f"⚡ **FLAXXI ENGINE**",
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(
                    message.chat.id,
                    "❌ **Sorry! No active keys available right now.**\nPlease ask the owner to add more keys in the admin panel.",
                    parse_mode="Markdown"
                )
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: Server connection timeout or issue.")
            print("Firebase Error:", e)
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
        InlineKeyboardButton("📋 View All Keys", callback_data="admin_view_keys"),
        InlineKeyboardButton("🗑️ Remove Key", callback_data="admin_remove_key")
    )
    
    bot.send_message(
        message.chat.id,
        "👑 **FLAXXI ENGINE - DPAdmin Panel**\n\nChoose an option:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# --- /remove COMMAND ---
@bot.message_handler(commands=['remove'])
def remove_command(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ **You are not authorized.**", parse_mode="Markdown")
        return

    msg = bot.send_message(
        message.chat.id,
        "🗑️ **Enter the key you want to remove:**",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, delete_key_from_firebase)

# --- CALLBACK QUERY HANDLER ---
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "admin_add_key":
        if call.from_user.id != OWNER_ID:
            return
        
        msg = bot.send_message(
            call.message.chat.id,
            "✍️ **Please send the key you want to add** (e.g., your DPAdmin key):",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, save_custom_key)
        
    elif call.data == "admin_view_keys":
        if call.from_user.id != OWNER_ID:
            return
        try:
            response = requests.get(f"{FIREBASE_URL}/keys.json", timeout=10)
            keys_data = response.json()
            if not keys_data:
                bot.send_message(call.message.chat.id, "📋 **No keys found in Firebase.**", parse_mode="Markdown")
            else:
                msg = "📋 **Firebase Keys List:**\n\n"
                items = keys_data.items() if isinstance(keys_data, dict) else enumerate(keys_data)
                for k_id, item in items:
                    if isinstance(item, dict):
                        k_val = item.get('key')
                        claimed_status = "🔴 Used" if item.get('claimed') else "🟢 Active"
                        msg += f"• `{k_val}` | {claimed_status}\n"
                bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Error fetching keys: {e}")

    elif call.data == "admin_remove_key":
        if call.from_user.id != OWNER_ID:
            return
        
        msg = bot.send_message(
            call.message.chat.id,
            "🗑️ **Enter the key you want to remove:**",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(msg, delete_key_from_firebase)

# --- SAVE CUSTOM KEY FUNCTION ---
def save_custom_key(message):
    if message.from_user.id != OWNER_ID:
        return
    
    custom_key = message.text.strip()
    
    data = {
        "key": custom_key,
        "status": "ACTIVE",
        "claimed": False
    }
    
    try:
        requests.post(f"{FIREBASE_URL}/keys.json", json=data, timeout=10)
        bot.send_message(
            message.chat.id,
            f"✅ **Key Successfully Saved to Firebase!**\n\n🔑 `{custom_key}`",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Failed to save key: {e}")

# --- DELETE KEY FROM FIREBASE FUNCTION ---
def delete_key_from_firebase(message):
    if message.from_user.id != OWNER_ID:
        return
    
    target_key = message.text.strip()
    
    try:
        response = requests.get(f"{FIREBASE_URL}/keys.json", timeout=10)
        keys_data = response.json()
        
        found = False
        if keys_data and isinstance(keys_data, dict):
            for k_id, item in keys_data.items():
                if isinstance(item, dict) and item.get("key") == target_key:
                    # Delete the key matching the input
                    requests.delete(f"{FIREBASE_URL}/keys/{k_id}.json", timeout=10)
                    found = True
                    break
                    
        if found:
            bot.send_message(
                message.chat.id,
                f"🗑️ **Key removed successfully!**\n\n🔑 `{target_key}`",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(
                message.chat.id,
                f"❌ **Key not found in Firebase database:**\n`{target_key}`",
                parse_mode="Markdown"
            )
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error removing key: {e}")

# Bot ko run rakhne ke liye
bot.infinity_polling()
