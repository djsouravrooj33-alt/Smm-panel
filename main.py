import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    filters,
)
from database import is_admin
from keyboards import main_menu, admin_panel, owner_panel
from handlers import admin, user, payment

OWNER_ID = 8145485145
BOT_TOKEN = os.environ.get("BOT_TOKEN")


async def start(update: Update, context):
    uid = update.effective_user.id
    await update.message.reply_text(
        "স্বাগতম! মেনু থেকে বেছে নিন:",
        reply_markup=main_menu(is_admin(uid, OWNER_ID), uid == OWNER_ID)
    )


async def owner_panel_cmd(update: Update, context):
    if update.effective_user.id == OWNER_ID:
        await update.message.reply_text("Owner Panel:", reply_markup=owner_panel())


async def admin_panel_cmd(update: Update, context):
    if is_admin(update.effective_user.id, OWNER_ID):
        await update.message.reply_text("Admin Panel:", reply_markup=admin_panel())


def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # ---------- Owner Conversation ----------
    owner_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Set Admin$"), admin.set_admin_start),
            MessageHandler(filters.Regex("^Add Balance$"), payment.add_balance_start),
            MessageHandler(filters.Regex("^Set UPI Pic$"), payment.set_upi_pic_start),
        ],
        states={
            admin.ASK_ADMIN_ID: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin.set_admin_done)
            ],
            payment.ASK_ADD_BAL_USER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, payment.add_balance_user)
            ],
            payment.ASK_ADD_BAL_AMT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, payment.add_balance_amount)
            ],
            payment.ASK_UPI_PIC: [
                MessageHandler(filters.PHOTO, payment.set_upi_pic_done)
            ],
        },
        fallbacks=[]
    )

    # ---------- Admin Conversation (Add / Remove Account) ----------
    admin_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^Add Account$"), admin.add_acc_start),
            MessageHandler(filters.Regex("^Remove Account$"), admin.remove_acc_start),
        ],
        states={
            admin.ASK_PHONE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin.add_acc_phone)
            ],
            admin.ASK_PASS: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin.add_acc_pass)
            ],
            admin.ASK_REMOVE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin.remove_acc_done)
            ],
        },
        fallbacks=[]
    )

    # ---------- User Order Conversation ----------
    order_conv = ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^(Add Followers|Add Like|Add Comment)$"),
                user.order_start
            )
        ],
        states={
            user.ASK_COUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, user.order_count)
            ],
            user.ASK_TARGET: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, user.order_target)
            ],
            user.ASK_COMMENT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, user.order_comment)
            ],
        },
        fallbacks=[]
    )

    # ---------- সাধারণ হ্যান্ডলার ----------
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex("^Owner Panel$"), owner_panel_cmd))
    app.add_handler(MessageHandler(filters.Regex("^Admin Panel$"), admin_panel_cmd))
    app.add_handler(MessageHandler(filters.Regex("^Check Accounts$"), admin.check_acc))
    app.add_handler(MessageHandler(filters.Regex("^Balance$"), payment.show_balance))
    app.add_handler(MessageHandler(filters.Regex("^Deposit$"), payment.deposit))

    # ---------- Conversation হ্যান্ডলার ----------
    app.add_handler(owner_conv)
    app.add_handler(admin_conv)
    app.add_handler(order_conv)

    # ---------- Payment proof (ছবি) ----------
    app.add_handler(MessageHandler(filters.PHOTO, payment.handle_payment_proof))

    # ---------- Render Webhook ----------
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
