from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from database import is_admin, add_admin, get_accounts, add_account, remove_account

OWNER_ID = 8145485145

ASK_PHONE, ASK_PASS, ASK_ADMIN_ID = range(3)

# ---------- Owner: Set Admin ----------
async def set_admin_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("Admin-এর Telegram User ID দিন:")
    return ASK_ADMIN_ID

async def set_admin_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        new_admin = int(update.message.text)
        add_admin(new_admin)
        await update.message.reply_text(f"✅ {new_admin} কে Admin করা হয়েছে।")
    except Exception:
        await update.message.reply_text("❌ ভুল ID।")
    return ConversationHandler.END

# ---------- Admin: Accounts ----------
async def add_acc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, OWNER_ID):
        return
    await update.message.reply_text("Instagram Phone/Username দিন:")
    return ASK_PHONE

async def add_acc_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("Password দিন:")
    return ASK_PASS

async def add_acc_pass(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_account(context.user_data["phone"], update.message.text)
    await update.message.reply_text("✅ অ্যাকাউন্ট যোগ হয়েছে।")
    return ConversationHandler.END

async def remove_acc_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, OWNER_ID):
        return
    await update.message.reply_text("Phone ও Password একসাথে পাঠান (স্পেস দিয়ে):")
    return ASK_PHONE

async def remove_acc_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    parts = update.message.text.split()
    if len(parts) >= 2:
        remove_account(parts[0], parts[1])
        await update.message.reply_text("✅ রিমুভ হয়েছে।")
    else:
        await update.message.reply_text("❌ ফরম্যাট ভুল।")
    return ConversationHandler.END

async def check_acc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, OWNER_ID):
        return
    accs = get_accounts()
    await update.message.reply_text(f"📊 মোট অ্যাকাউন্ট: {len(accs)}")
