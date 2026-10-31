import os
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from database import get_balance, add_balance, get_setting, set_setting

OWNER_ID = 8145485145
OWNER_USERNAME = "@amane_loyal_me"

ASK_ADD_BAL_USER, ASK_ADD_BAL_AMT, ASK_UPI_PIC = range(10, 13)

# ---------- Owner: Add Balance ----------
async def add_balance_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("User ID দিন:")
    return ASK_ADD_BAL_USER

async def add_balance_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["target_user"] = int(update.message.text)
    await update.message.reply_text("কত টাকা যোগ করবেন? (শুধু সংখ্যা)")
    return ASK_ADD_BAL_AMT

async def add_balance_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    amount = int(update.message.text)
    target = context.user_data["target_user"]
    add_balance(target, amount)
    await update.message.reply_text(f"✅ {target} এর ব্যালেন্সে {amount} টাকা যোগ হয়েছে।")
    try:
        await context.bot.send_message(target, f"✅ আপনার ব্যালেন্সে {amount} টাকা যোগ হয়েছে।")
    except Exception:
        pass
    return ConversationHandler.END

# ---------- Owner: Set UPI Pic ----------
async def set_upi_pic_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("UPI-র স্ক্রিনশট বা ছবি পাঠান:")
    return ASK_UPI_PIC

async def set_upi_pic_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    set_setting("upi_pic", photo.file_id)
    await update.message.reply_text("✅ UPI ছবি সেভ হয়েছে।")
    return ConversationHandler.END

# ---------- User: Balance & Deposit ----------
async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bal = get_balance(update.effective_user.id)
    await update.message.reply_text(f"💰 আপনার ব্যালেন্স: {bal} টাকা")

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    upi = "rooj@fam"
    text = (
        f"💳 UPI: `{upi}`\n\n"
        f"পেমেন্ট করে স্ক্রিনশট পাঠান।\nOwner: {OWNER_USERNAME}\n\n"
        f"⏳ সময়: ২-৪ ঘণ্টা"
    )
    pic = get_setting("upi_pic")
    if pic:
        await update.message.reply_photo(photo=pic, caption=text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")

async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await context.bot.forward_message(
        chat_id=OWNER_ID,
        from_chat_id=update.message.chat_id,
        message_id=update.message.message_id
    )
    await context.bot.send_message(
        OWNER_ID,
        f"📩 Payment proof from {user.first_name} (@{user.username})\nUser ID: {user.id}"
    )
    await update.message.reply_text(
        "✅ পাঠানো হয়েছে। Owner যোগাযোগ করবেন।\n"
        f"Owner: {OWNER_USERNAME}\n⏳ ২-৪ ঘণ্টা অপেক্ষা করুন।"
    )
