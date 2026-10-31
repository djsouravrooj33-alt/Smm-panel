import os
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler
)
from database import (
    get_balance, add_balance, is_admin, add_admin,
    get_accounts, add_account, remove_account,
    get_setting, set_setting
)
from instagram import do_follow, do_like, do_comment
from keyboards import main_menu, admin_panel, owner_panel, confirm_inline

OWNER_ID = 8145485145
OWNER_USERNAME = "@amane_loyal_me"
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Conversation states
ASK_PHONE, ASK_PASS, ASK_TARGET, ASK_COUNT, ASK_COMMENT = range(5)
ASK_ADMIN_ID, ASK_ADD_BAL_USER, ASK_ADD_BAL_AMT, ASK_UPI_PIC = range(10, 14)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    admin_flag = is_admin(user_id, OWNER_ID)
    await update.message.reply_text(
        "স্বাগতম! মেনু থেকে বেছে নিন:",
        reply_markup=main_menu(admin_flag, user_id == OWNER_ID)
    )

# ---------- Owner ----------
async def owner_panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("Owner Panel:", reply_markup=owner_panel())

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
    except:
        await update.message.reply_text("❌ ভুল ID।")
    return ConversationHandler.END

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
    # ইউজারকে জানান
    try:
        await context.bot.send_message(target, f"✅ আপনার ব্যালেন্সে {amount} টাকা যোগ হয়েছে।")
    except:
        pass
    return ConversationHandler.END

async def set_upi_pic_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return
    await update.message.reply_text("UPI-র স্ক্রিনশট বা ছবি পাঠান:")
    return ASK_UPI_PIC

async def set_upi_pic_done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file_id = photo.file_id
    set_setting("upi_pic", file_id)
    await update.message.reply_text("✅ UPI ছবি সেভ হয়েছে।")
    return ConversationHandler.END

# ---------- Admin (Accounts) ----------
async def admin_panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id, OWNER_ID):
        return
    await update.message.reply_text("Admin Panel:", reply_markup=admin_panel())

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

# ---------- User (Orders) ----------
async def order_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "Follow" in text:
        context.user_data["order_type"] = "follow"
    elif "Like" in text:
        context.user_data["order_type"] = "like"
    elif "Comment" in text:
        context.user_data["order_type"] = "comment"
    else:
        return
    await update.message.reply_text("কতগুলো চান? (সংখ্যা দিন, যেমন 10)")
    return ASK_COUNT

async def order_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["count"] = int(update.message.text)
    await update.message.reply_text("Target Username অথবা Post Link দিন:")
    return ASK_TARGET

async def order_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["target"] = update.message.text
    order_type = context.user_data["order_type"]
    count = context.user_data["count"]
    user_id = update.effective_user.id

    # দাম হিসাব (আপনার দেওয়া দাম অনুযায়ী)
    price_map = {"follow": 5, "like": 4, "comment": 3}
    cost = price_map[order_type] * (count // 10)
    if cost == 0:
        cost = price_map[order_type]  # মিনিমাম ১০ এর জন্য

    balance = get_balance(user_id)
    if balance < cost:
        await update.message.reply_text(f"❌ ব্যালেন্স কম। প্রয়োজন {cost} টাকা, আছে {balance} টাকা।")
        return ConversationHandler.END

    if order_type == "comment":
        await update.message.reply_text("কী কমেন্ট লিখবেন? (যেমন: nice)")
        return ASK_COMMENT

    # Follow/Like সরাসরি চালান
    add_balance(user_id, -cost)  # ব্যালেন্স কাটুন
    await update.message.reply_text("⏳ প্রসেস হচ্ছে...")
    if order_type == "follow":
        done = do_follow(context.user_data["target"], count)
    else:
        done = do_like(context.user_data["target"], count)
    await update.message.reply_text(f"✅ {done}টি {order_type} সম্পন্ন হয়েছে।")
    return ConversationHandler.END

async def order_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    comment_text = update.message.text
    count = context.user_data["count"]
    target = context.user_data["target"]
    user_id = update.effective_user.id
    cost = 3 * (count // 10) or 3
    add_balance(user_id, -cost)
    await update.message.reply_text("⏳ কমেন্ট প্রসেস হচ্ছে...")
    done = do_comment(target, comment_text, count)
    await update.message.reply_text(f"✅ {done}টি কমেন্ট সম্পন্ন হয়েছে।")
    return ConversationHandler.END

# ---------- Balance & Deposit ----------
async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    bal = get_balance(update.effective_user.id)
    await update.message.reply_text(f"💰 আপনার ব্যালেন্স: {bal} টাকা")

async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    upi = "rooj@fam"
    text = f"💳 UPI: `{upi}`\n\nপেমেন্ট করে স্ক্রিনশট পাঠান।\nOwner: {OWNER_USERNAME}\n\n⏳ সময়: ২-৪ ঘণ্টা"
    pic = get_setting("upi_pic")
    if pic:
        await update.message.reply_photo(photo=pic, caption=text, parse_mode="Markdown")
    else:
        await update.message.reply_text(text, parse_mode="Markdown")

# ---------- Payment Forward ----------
async def handle_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ইউজার ছবি পাঠালে Owner-কে ফরওয়ার্ড
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
    await update.message.reply_text("✅ পাঠানো হয়েছে। Owner যোগাযোগ করবেন।")

# ---------- Main ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Owner conversations
    owner_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Set Admin$"), set_admin_start),
            MessageHandler(filters.Regex("^Add Balance$"), add_balance_start),
            MessageHandler(filters.Regex("^Set UPI Pic$"), set_upi_pic_start),
        ],
        states={
            ASK_ADMIN_ID: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_admin_done)],
            ASK_ADD_BAL_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_balance_user)],
            ASK_ADD_BAL_AMT: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_balance_amount)],
            ASK_UPI_PIC: [MessageHandler(filters.PHOTO, set_upi_pic_done)],
        },
        fallbacks=[]
    )

    # Admin conversations
    admin_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Add Account$"), add_acc_start),
            MessageHandler(filters.Regex("^Remove Account$"), remove_acc_start),
        ],
        states={
            ASK_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_acc_phone)],
            ASK_PASS: [MessageHandler(filters.TEXT & ~filters.COMMAND, add_acc_pass)],
        },
        fallbacks=[]
    )

    # User order conversations
    order_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^(Add Followers|Add Like|Add Comment)$"), order_start)
        ],
        states={
            ASK_COUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_count)],
            ASK_TARGET: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_target)],
            ASK_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, order_comment)],
        },
        fallbacks=[]
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^Owner Panel$"), owner_panel_cmd))
    app.add_handler(MessageHandler(filters.Regex("^Admin Panel$"), admin_panel_cmd))
    app.add_handler(MessageHandler(filters.Regex("^Check Accounts$"), check_acc))
    app.add_handler(MessageHandler(filters.Regex("^Balance$"), show_balance))
    app.add_handler(MessageHandler(filters.Regex("^Deposit$"), deposit))
    app.add_handler(owner_conv)
    app.add_handler(admin_conv)
    app.add_handler(order_conv)
    app.add_handler(MessageHandler(filters.PHOTO, handle_payment_proof))

    # Render-এ Webhook চালাতে হবে
    port = int(os.environ.get("PORT", 10000))
    webhook_url = os.environ.get("WEBHOOK_URL")
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        url_path="/webhook",
        webhook_url=f"{webhook_url}/webhook"
    )

if __name__ == "__main__":
    main()
