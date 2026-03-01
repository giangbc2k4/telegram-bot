import os
import requests
import pandas as pd
import matplotlib.pyplot as plt

from io import StringIO
from datetime import datetime, timedelta, time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

SHEET_CSV = "https://docs.google.com/spreadsheets/d/1GjDK8knbs-JuPNsP125vqEXmoIBb9Pu_4kFAOATCEuA/export?format=csv&gid=0"


# ================= LOAD DATA =================

def load_sheet():
    r = requests.get(SHEET_CSV)
    df = pd.read_csv(StringIO(r.text))
    return df


# ================= DRAW TIMELINE =================

def draw_timeline(df, target_date, filename):

    df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
    df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")

    # Lọc đúng ngày
    start_day = datetime.combine(target_date, time.min)
    end_day = datetime.combine(target_date, time.max)

    df = df[(df["start_time"] <= end_day) & (df["end_time"] >= start_day)]

    if df.empty:
        return False

    rooms = df["room"].unique()

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, room in enumerate(rooms):
        room_data = df[df["room"] == room]

        for _, row in room_data.iterrows():

            start = max(row["start_time"], start_day)
            end = min(row["end_time"], end_day)

            start_hour = (
                start.hour
                + start.minute / 60
                + start.second / 3600
            )

            duration_hours = (end - start).total_seconds() / 3600

            ax.barh(
                y=i,
                width=duration_hours,
                left=start_hour,
                height=0.4,
            )

    ax.set_yticks(range(len(rooms)))
    ax.set_yticklabels(rooms)
    ax.set_xlim(0, 24)
    ax.set_xlabel("Giờ trong ngày")
    ax.set_title(f"Timeline {target_date.strftime('%d/%m/%Y')}")

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

    return True


# ================= COMMANDS =================

async def timeline_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = load_sheet()
    today = datetime.now().date()

    ok = draw_timeline(df, today, "today.png")

    if not ok:
        await update.message.reply_text("Hôm nay không có dữ liệu.")
        return

    await update.message.reply_photo(photo=open("today.png", "rb"))


async def timeline_yesterday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = load_sheet()
    yesterday = (datetime.now() - timedelta(days=1)).date()

    ok = draw_timeline(df, yesterday, "yesterday.png")

    if not ok:
        await update.message.reply_text("Hôm qua không có dữ liệu.")
        return

    await update.message.reply_photo(photo=open("yesterday.png", "rb"))


# ================= RUN BOT =================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("timeline_today", timeline_today))
app.add_handler(CommandHandler("timeline_yesterday", timeline_yesterday))

app.run_polling()
