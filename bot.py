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
    await update.message.reply_text(
        f"Chat ID của bạn là: {update.effective_chat.id}"
    )


# ================= TIMELINE TODAY =================
async def timeline(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        await update.message.reply_text("1️⃣ Bắt đầu timeline")

        chat_id = update.effective_chat.id
        await update.message.reply_text(f"Chat ID: {chat_id}")

        # đọc CSV
        df = pd.read_csv(SHEET_CSV)
        await update.message.reply_text("2️⃣ Đọc CSV thành công")

        await update.message.reply_text(f"Số dòng: {len(df)}")

        # kiểm tra cột
        await update.message.reply_text(f"Cột trong sheet: {list(df.columns)}")

        # ép kiểu
        df["ChatID"] = df["ChatID"].astype(str).str.strip()
        df["Start"] = pd.to_datetime(df["Start"], dayfirst=True, errors="coerce")
        df["End"] = pd.to_datetime(df["End"], dayfirst=True, errors="coerce")

        await update.message.reply_text("3️⃣ Parse datetime xong")

        # lọc chatid
        df = df[df["ChatID"] == str(chat_id)]
        await update.message.reply_text(f"Sau lọc chatid còn: {len(df)} dòng")

        # lọc hôm nay (UTC+7)
        today = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).date()
        df = df[df["Start"].dt.date == today]
        await update.message.reply_text(f"Sau lọc ngày còn: {len(df)} dòng")

        df = df.dropna(subset=["End"])

        if df.empty:
            await update.message.reply_text("❌ Không có dữ liệu hôm nay.")
            return

        await update.message.reply_text("4️⃣ Chuẩn bị vẽ biểu đồ")

        fig, ax = plt.subplots(figsize=(10, 5))

        for _, row in df.iterrows():
            start_sec = row["Start"].timestamp()
            end_sec = row["End"].timestamp()
            ax.barh(row["Room"], end_sec - start_sec, left=start_sec)

        ax.set_title("Timeline hôm nay")
        ax.invert_yaxis()

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
