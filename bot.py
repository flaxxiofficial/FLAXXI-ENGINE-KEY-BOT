import telebot
import random
import string
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Token (BotFather se mila hua token)
TOKEN = "8868351923:AAHK25ihjj6D40xnzpHm16OHuFonQJnUhzI"
bot = telebot.TeleBot(TOKEN)

# Aapki Telegram ID (Owner ID)
OWNER_ID = 6903735098

# Active keys store karne ke liye list
active_keys = []

# Random Key Generator Function
def generate_key(prefix="FLAXXI"):
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))
    return f"{prefix}-AimAi-{suffix}"

# --- /start COMMAND (Deep Link Handler) ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    args = message.text.split()
    
    # AGAR USER ADS COMPLETE KARKE WAPAS BOT MEIN AAYA HAI
    if len(args) > 1 and args[1] == "verify_claimkey":
        key = generate_key()
        active_keys.append({"key": key, "status": "ACTIVE"})
        
        bot.send_message(
            message.chat.id,
            f"🎉 **Verification Successful!**\n\n"
            f"🔑 **Your Key:**\n`{key}`\n\n"
            f"⏳ **Validity:** 24 Hours\n"
            f"⚡ **FLAXXI ENGINE**",
            parse_mode="Markdown"
        )
        return

    # NORMAL /start MESSAGE (Verification Link ke sath)
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    
    # Aapki ShrinkEarn Short Link yahan add kar di gayi hai
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
        active_keys.append({"key": new_key, "status": "ACTIVE"})
        bot.send_message(call.message.chat.id, f"✅ **VIP Key Created:** `{new_key}`", parse_mode="Markdown")
        
    elif call.data == "admin_view_keys":
        if call.from_user.id != OWNER_ID:
            return
        if not active_keys:
            bot.send_message(call.message.chat.id, "📋 No active keys.")
        else:
            msg = "📋 **Keys List:**\n\n"
            for item in active_keys:
                msg += f"• `{item['key']}`\n"
            bot.send_message(call.message.chat.id, msg, parse_mode="Markdown")

# Bot ko continuously run rakhne ke liye
bot.infinity_polling()
