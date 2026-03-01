from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import tempfile
import datetime

TOKEN = os.getenv("BOT_TOKEN")

SHEET_CSV = "https://docs.google.com/spreadsheets/d/1GjDK8knbs-JuPNsP125vqEXmoIBb9Pu_4kFAOATCEuA/export?format=csv&gid=0"


# ================= GET CHAT ID =================
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Chat ID của bạn là: {update.effective_chat.id}"
    )


# ================= TIMELINE HÔM NAY =================
async def timeline(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        chat_id = update.effective_chat.id

        # đọc dữ liệu
        df = pd.read_csv(SHEET_CSV)

        # chuẩn hóa tên cột (đề phòng viết thường)
        df.columns = df.columns.str.strip()

        # ép kiểu
        df["ChatID"] = df["ChatID"].astype(str).str.strip()
        df["Start"] = pd.to_datetime(df["Start"], dayfirst=True, errors="coerce")
        df["End"] = pd.to_datetime(df["End"], dayfirst=True, errors="coerce")

        # lọc đúng chatid
        df = df[df["ChatID"] == str(chat_id)]

        # lấy hôm nay theo UTC+7
        today = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).date()
        df = df[df["Start"].dt.date == today]

        # bỏ dòng chưa có End
        df = df.dropna(subset=["End"])

        if df.empty:
            await update.message.reply_text("❌ Không có dữ liệu hôm nay.")
            return

        # ================= VẼ =================
        fig, ax = plt.subplots(figsize=(10, 5))

        for _, row in df.iterrows():
            ax.barh(
                row["room"],
                row["End"] - row["Start"],
                left=row["Start"]
            )

        # format trục giờ
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        ax.xaxis.set_major_locator(mdates.HourLocator())

        # cố định từ 00:00 -> 23:59
        start_day = datetime.datetime.combine(today, datetime.time(0, 0, 0))
        end_day = datetime.datetime.combine(today, datetime.time(23, 59, 59))

        ax.set_xlim(start_day, end_day)

        ax.set_title("Timeline hôm nay")
        ax.invert_yaxis()
        plt.xticks(rotation=45)
        plt.tight_layout()

        # lưu file tạm
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        plt.savefig(tmp.name)
        plt.close()

        await update.message.reply_photo(photo=open(tmp.name, "rb"))

    except Exception as e:
        await update.message.reply_text(f"🚨 Lỗi: {str(e)}")


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("getid", get_id))
app.add_handler(CommandHandler("timeline", timeline))

app.run_polling()
