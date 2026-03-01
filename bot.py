from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tempfile
import datetime

TOKEN = os.getenv("BOT_TOKEN")

# 👉 Thay ID sheet của bạn
SHEET_CSV = "https://docs.google.com/spreadsheets/d/SPREADSHEET_ID/export?format=csv"

# 👉 Thay chat id của bạn
MY_CHAT_ID = -5047436625


# ================= GET CHAT ID =================
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(f"Chat ID của bạn là: {chat_id}")


# ================= VẼ TIMELINE =================
async def send_timeline(chat_id, context):

    df = pd.read_csv(SHEET_CSV)

    # đổi tên cột đúng với sheet của bạn
    df.columns = ["Room", "ChatID", "Start", "End", "Duration", "Status", "LastSeen", "Telegram"]

    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["End"] = pd.to_datetime(df["End"], errors="coerce")

    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    df = df[df["Start"].dt.date == yesterday]
    df = df[df["ChatID"] == chat_id]
    df = df.dropna(subset=["End"])

    if df.empty:
        await context.bot.send_message(chat_id, "Không có dữ liệu hôm qua.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))

    for _, row in df.iterrows():
        start_sec = row["Start"].timestamp()
        end_sec = row["End"].timestamp()

        ax.barh(
            row["Room"],
            end_sec - start_sec,
            left=start_sec
        )

    ax.set_title(f"Timeline {yesterday.strftime('%d/%m/%Y')}")
    ax.invert_yaxis()

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(tmp.name)
    plt.close()

    await context.bot.send_photo(chat_id=chat_id, photo=open(tmp.name, "rb"))


# ================= COMMAND TEST =================
async def timeline_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await send_timeline(update.effective_chat.id, context)


# ================= AUTO JOB =================
async def daily_job(context: ContextTypes.DEFAULT_TYPE):
    await send_timeline(MY_CHAT_ID, context)


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("getid", get_id))
app.add_handler(CommandHandler("timeline", timeline_cmd))

# gửi mỗi ngày lúc 00:05
app.job_queue.run_daily(
    daily_job,
    time=datetime.time(hour=0, minute=5)
)

app.run_polling()
