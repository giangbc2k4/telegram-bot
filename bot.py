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

# Link CSV của Google Sheet
SHEET_CSV = "https://docs.google.com/spreadsheets/d/1GjDK8knbs-JuPNsP125vqEXmoIBb9Pu_4kFAOATCEuA/export?format=csv"


# ================= GET CHAT ID =================
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Chat ID của bạn là: {update.effective_chat.id}")


# ================= TIMELINE =================
async def timeline(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    df = pd.read_csv(SHEET_CSV)

    # Đặt lại tên cột đúng theo sheet của bạn
    df.columns = ["Room", "ChatID", "Start", "End", "Duration", "Status", "LastSeen", "Telegram"]

    df["Start"] = pd.to_datetime(df["Start"], errors="coerce")
    df["End"] = pd.to_datetime(df["End"], errors="coerce")

    # Lọc theo chatid
    df = df[df["ChatID"] == chat_id]
    df = df.dropna(subset=["End"])

    if df.empty:
        await update.message.reply_text("Không có dữ liệu.")
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

    ax.set_title("Timeline hoạt động")
    ax.invert_yaxis()

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    plt.savefig(tmp.name)
    plt.close()

    await update.message.reply_photo(photo=open(tmp.name, "rb"))


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("getid", get_id))
app.add_handler(CommandHandler("timeline", timeline))

app.run_polling()
