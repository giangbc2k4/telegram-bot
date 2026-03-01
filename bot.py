from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tempfile
from datetime import datetime, timedelta, time

TOKEN = os.getenv("BOT_TOKEN")

SHEET_CSV = "https://docs.google.com/spreadsheets/d/1GjDK8knbs-JuPNsP125vqEXmoIBb9Pu_4kFAOATCEuA/export?format=csv&gid=0"


# ================= GET CHAT ID =================
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID của bạn là: {update.effective_chat.id}")


# ================= LOAD DATA =================
def load_data():
    df = pd.read_csv(SHEET_CSV)
    df.columns = ["Room", "ChatID", "Start", "End", "Duration", "Status", "LastSeen", "Telegram"]

    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["End"] = pd.to_datetime(df["End"], errors="coerce")

    return df


# ================= DRAW TIMELINE =================
def draw_timeline(df, chat_id, target_date):

    start_day = datetime.combine(target_date, time.min)
    end_day = datetime.combine(target_date, time.max)

    # Lọc đúng chatid
    df = df[df["ChatID"] == chat_id]

    # Lọc đúng ngày (cắt đoạn giao nhau)
    df = df[(df["Start"] <= end_day) & (df["End"] >= start_day)]
    df = df.dropna(subset=["End"])

    if df.empty:
        return None

    fig, ax = plt.subplots(figsize=(12, 6))

    rooms = df["Room"].unique()

    for i, room in enumerate(rooms):
        room_data = df[df["Room"] == room]

        for _, row in room_data.iterrows():

            real_start = max(row["Start"], start_day)
            real_end = min(row["End"], end_day)

            start_hour = (
                real_start.hour +
                real_start.minute / 60 +
                real_start.second / 3600
            )

            duration_hours = (real_end - real_start).total_seconds() / 3600

            ax.barh(
                y=i,
                width=duration_hours,
                left=start_hour,
                height=0.4
            )

    ax.set_yticks(range(len(rooms)))
    ax.set_yticklabels(rooms)
    ax.set_xlim(0, 24)
    ax.set_xlabel("Giờ trong ngày")
    ax.set_title(f"Timeline {target_date.strftime('%d/%m/%Y')}")

    plt.tight_layout()

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(tmp.name)
    plt.close()

    return tmp.name


# ================= COMMANDS =================

async def timeline_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    df = load_data()
    today = datetime.now().date()

    img = draw_timeline(df, chat_id, today)

    if not img:
        await update.message.reply_text("Hôm nay không có dữ liệu.")
        return

    await update.message.reply_photo(photo=open(img, "rb"))


async def timeline_yesterday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    df = load_data()
    yesterday = (datetime.now() - timedelta(days=1)).date()

    img = draw_timeline(df, chat_id, yesterday)

    if not img:
        await update.message.reply_text("Hôm qua không có dữ liệu.")
        return

    await update.message.reply_photo(photo=open(img, "rb"))


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("getid", get_id))
app.add_handler(CommandHandler("timeline_today", timeline_today))
app.add_handler(CommandHandler("timeline_yesterday", timeline_yesterday))

app.run_polling()
