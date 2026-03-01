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
        await update.message.reply_text("=== DEBUG TIMELINE ===")

        chat_id = update.effective_chat.id
        chat_id_str = str(chat_id).strip()

        await update.message.reply_text(f"Chat ID bot: {chat_id_str}")

        # ====== ĐỌC CSV ======
        df = pd.read_csv(SHEET_CSV)

        await update.message.reply_text(f"Tổng dòng trong sheet: {len(df)}")
        await update.message.reply_text(f"Cột trong sheet: {list(df.columns)}")

        # ====== RENAME CỘT ======
        df = df.rename(columns={
            "room": "Room",
            "room.1": "ChatID",
            "ChatID": "ChatID",
            "start_time": "Start",
            "Start": "Start",
            "end_time": "End",
            "End": "End",
            "duration": "Duration",
            "status": "Status",
            "last_seen": "LastSeen"
        })

        if "ChatID" not in df.columns:
            await update.message.reply_text("🚨 Không tìm thấy cột ChatID.")
            return

        # ====== XỬ LÝ CHATID ======
        df["ChatID"] = (
            df["ChatID"]
            .astype(str)
            .str.replace(".0", "", regex=False)
            .str.strip()
        )

        await update.message.reply_text(
            f"ChatID trong sheet: {df['ChatID'].unique()}"
        )

        # ====== PARSE DATETIME ======
        if "Start" not in df.columns:
            await update.message.reply_text("🚨 Không tìm thấy cột Start.")
            return

        df["Start"] = pd.to_datetime(df["Start"], dayfirst=True, errors="coerce")

        await update.message.reply_text(
            f"Ngày có trong sheet: {df['Start'].dt.date.unique()}"
        )

        # ====== LỌC THEO CHATID ======
        df_chat = df[df["ChatID"] == chat_id_str]
        await update.message.reply_text(
            f"Sau lọc chatid còn: {len(df_chat)} dòng"
        )

        # ====== LỌC HÔM NAY (UTC+7) ======
        today = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).date()
        await update.message.reply_text(f"Hôm nay (UTC+7): {today}")

        df_today = df_chat[df_chat["Start"].dt.date == today]
        await update.message.reply_text(
            f"Sau lọc ngày hôm nay còn: {len(df_today)} dòng"
        )

        if df_today.empty:
            await update.message.reply_text("❌ Không có dữ liệu khớp.")
        else:
            await update.message.reply_text("✅ Có dữ liệu rồi.")

    except Exception as e:
        await update.message.reply_text(f"🚨 Lỗi: {str(e)}")


# ================= MAIN =================
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("getid", get_id))
app.add_handler(CommandHandler("timeline", timeline))

app.run_polling()
