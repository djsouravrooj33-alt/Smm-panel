from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters
from database import get_balance, add_balance
from instagram import do_follow, do_like, do_comment

ASK_TARGET, ASK_COUNT, ASK_COMMENT = range(3, 6)

PRICE_MAP = {"follow": 5, "like": 4, "comment": 3}

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

    cost = PRICE_MAP[order_type] * (count // 10)
    if cost == 0:
        cost = PRICE_MAP[order_type]

    balance = get_balance(user_id)
    if balance < cost:
        await update.message.reply_text(
            f"❌ ব্যালেন্স কম। প্রয়োজন {cost} টাকা, আছে {balance} টাকা।"
        )
        return ConversationHandler.END

    if order_type == "comment":
        await update.message.reply_text("কী কমেন্ট লিখবেন? (যেমন: nice)")
        return ASK_COMMENT

    add_balance(user_id, -cost)
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
