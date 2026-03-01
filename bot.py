from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

TOKEN = os.getenv("BOT_TOKEN")

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID của bạn là: {chat_id}")

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("getid", get_id))

app.run_polling()