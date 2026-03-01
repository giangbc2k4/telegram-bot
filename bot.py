from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
import pandas as pd
import datetime

TOKEN = os.getenv("BOT_TOKEN")

SHEET_CSV = "https://docs.google.com/spreadsheets/d/1GjDK8knbs-JuPNsP125vqEXmoIBb9Pu_4kFAOATCEuA/export?format=csv&gid=0"


# ================= GET CHAT ID =================
async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Chat ID của bạn là: {update.effective_chat.id}"
    )


# ================= DEBUG TIMELINE =================
async def timeline(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        await update.message.reply_text("1️⃣ Bắt đầu timeline")

        chat_id = update.effective_chat.id
        await update.message.reply_text(f"Chat ID: {chat_id}")

        # đọc CSV
        df = pd.read_csv(SHEET_CSV)
        await update.message.reply_text("2️⃣ Đọc CSV thành công")
        await update.message.reply_text(f"Số dòng: {len(df)}")
        await update.message.reply_text(f"Cột trong sheet: {list(df.columns)}")

        # ===== DEBUG: In toàn bộ ChatID trong sheet =====
        await update.message.reply_text(
            f"Tất cả ChatID trong sheet:\n{df['ChatID'].unique()}"
        )

        # ép kiểu
        df["ChatID"] = (
            df["ChatID"]
            .astype(str)
            .str.replace(".0", "", regex=False)
            .str.strip()
        )

        df["Start"] = pd.to_datetime(df["Start"], dayfirst=True, errors="coerce")
        df["End"] = pd.to_datetime(df["End"], dayfirst=True, errors="coerce")

        await update.message.reply_text("3️⃣ Parse datetime xong")

        # ===== DEBUG: In 5 dòng đầu =====
        preview = df.head(5).to_string()
        await update.message.reply_text(f"5 dòng đầu:\n{preview}")

        # lọc chatid
        df_chat = df[df["ChatID"] == str(chat_id)]
        await update.message.reply_text(f"Sau lọc chatid còn: {len(df_chat)} dòng")

        if df_chat.empty:
            await update.message.reply_text("🚨 Không match được ChatID.")
            return

        # ===== DEBUG: xem ngày trong dữ liệu của chat này =====
        await update.message.reply_text(
            f"Ngày có trong dữ liệu chat này:\n{df_chat['Start'].dt.date.unique()}"
        )

        # lọc hôm nay (UTC+7)
        today = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).date()
        await update.message.reply_text(f"Hôm nay (UTC+7): {today}")

        df_today = df_chat[df_chat["Start"].dt.date == today]
        await update.message.reply_text(f"Sau lọc ngày còn: {len(df_today)} dòng")

        if df_today.empty:
            await update.message.reply_text("❌ Có dữ liệu nhưng không phải hôm nay.")
            return

        df_today = df_today.dropna(subset=["End"])

        if df_today.empty:
            await update.message.reply_text("❌ Có Start nhưng chưa có End.")
            return

        await update.message.reply_text("4️⃣ Dữ liệu hợp lệ, chuẩn bị vẽ")

        # ===== VẼ =====
        import matplotlib.pyplot as plt
        import tempfile

        fig, ax = plt.subplots(figsize=(10, 5))

        for _, row in df_today.iterrows():
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
