from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu(is_admin_user=False, is_owner=False):
    keyboard = [
        ["👤 Add Followers", "❤️ Add Like", "💬 Add Comment"],
        ["💰 Balance", "💳 Deposit"]
    ]
    if is_owner:
        keyboard.append(["👑 Owner Panel"])
    elif is_admin_user:
        keyboard.append(["🛠️ Admin Panel"])
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_panel():
    keyboard = [
        ["➕ Add Account", "➖ Remove Account"],
        ["📊 Check Accounts"],
        ["🔙 Back"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def owner_panel():
    keyboard = [
        ["👤 Set Admin", "💵 Add Balance"],
        ["🖼️ Set UPI Pic"],
        ["🔙 Back"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def confirm_inline(action: str):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}"),
         InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ])
