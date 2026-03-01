from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tempfile
import datetime

TOKEN = os.getenv("BOT_TOKEN")

SHEET_CSV = "https://docs.google.com/spreadsheets/d/1GjDK8knbs-JuPNsP125vqEXmoIBb9Pu_4kFAOATCEuA/export?format=csv&gid=0"


# ================= GET CHAT ID =================
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID của bạn là: {update.effective_chat.id}")


# ================= LOAD DATA =================
def load_data():
    df = pd.read_csv(SHEET_CSV)

    df.columns = [
        "Room",
        "ChatID",
        "Start",
        "End",
        "Duration",
        "Status",
        "LastSeen"
    ]

    df["Start"] = pd.to_datetime(df["Start"], dayfirst=True, errors="coerce")
    df["End"] = pd.to_datetime(df["End"], dayfirst=True, errors="coerce")
    df["ChatID"] = df["ChatID"].astype(str)

    return df


# ================= DRAW FUNCTION =================
async def draw_timeline(update: Update, context: ContextTypes.DEFAULT_TYPE, target_date):

    chat_id = str(update.effective_chat.id)
    df = load_data()

    df = df[df["ChatID"] == chat_id]
    df = df.dropna(subset=["Start", "End"])

    if df.empty:
        await update.message.reply_text("Không có dữ liệu.")
        return

    start_day = datetime.datetime.combine(target_date, datetime.time.min)
    end_day = datetime.datetime.combine(target_date, datetime.time.max)

    df = df[(df["Start"] >= start_day) & (df["Start"] <= end_day)]

    if df.empty:
        await update.message.reply_text("Không có dữ liệu trong ngày này.")
        return

    fig, ax = plt.subplots(figsize=(12, 6))

    for _, row in df.iterrows():
        start_sec = row["Start"].timestamp()
        end_sec = row["End"].timestamp()

        ax.barh(
            row["Room"],
            end_sec - start_sec,
            left=start_sec
        )

    ax.set_title(f"Timeline {target_date.strftime('%d/%m/%Y')}")
    ax.invert_yaxis()

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(tmp.name)
    plt.close()

    await update.message.reply_photo(photo=open(tmp.name, "rb"))


# ================= COMMANDS =================
async def timeline_today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today()
    await draw_timeline(update, context, today)


async def timeline_yesterday(update: Update, context: ContextTypes.DEFAULT_TYPE):
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    await draw_timeline(update, context, yesterday)


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("getid", get_id))
app.add_handler(CommandHandler("timeline_today", timeline_today))
app.add_handler(CommandHandler("timeline_yesterday", timeline_yesterday))

app.run_polling()
