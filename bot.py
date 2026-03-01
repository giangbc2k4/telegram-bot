async def timeline(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:
        await update.message.reply_text("=== DEBUG TIMELINE ===")

        chat_id = update.effective_chat.id
        chat_id_str = str(chat_id).strip()

        await update.message.reply_text(f"Chat ID bot: {chat_id_str}")

        # Đọc CSV
        df = pd.read_csv(SHEET_CSV)
        await update.message.reply_text(f"Tổng dòng trong sheet: {len(df)}")
        await update.message.reply_text(f"Cột: {list(df.columns)}")

        # Rename đúng theo header bạn đang có
        df = df.rename(columns={
            "room": "Room",
            "ChatID": "ChatID",
            "start_time": "Start",
            "end_time": "End",
            "duration": "Duration",
            "status": "Status",
            "last_seen": "LastSeen"
        })

        # Xử lý ChatID
        df["ChatID"] = (
            df["ChatID"]
            .astype(str)
            .str.replace(".0", "", regex=False)
            .str.strip()
        )

        await update.message.reply_text(
            f"ChatID trong sheet: {df['ChatID'].unique()}"
        )

        # Parse datetime
        df["Start"] = pd.to_datetime(df["Start"], dayfirst=True, errors="coerce")
        df["End"] = pd.to_datetime(df["End"], dayfirst=True, errors="coerce")

        await update.message.reply_text(
            f"Ngày có trong sheet: {df['Start'].dt.date.unique()}"
        )

        # Lọc theo ChatID
        df_chat = df[df["ChatID"] == chat_id_str]
        await update.message.reply_text(
            f"Sau lọc chatid: {len(df_chat)} dòng"
        )

        # Lọc hôm nay (UTC+7)
        today = (datetime.datetime.utcnow() + datetime.timedelta(hours=7)).date()
        await update.message.reply_text(f"Hôm nay (UTC+7): {today}")

        df_today = df_chat[df_chat["Start"].dt.date == today]
        await update.message.reply_text(
            f"Sau lọc ngày hôm nay: {len(df_today)} dòng"
        )

        if df_today.empty:
            await update.message.reply_text("❌ Không có dữ liệu khớp.")
        else:
            await update.message.reply_text("✅ Có dữ liệu rồi.")

    except Exception as e:
        await update.message.reply_text(f"🚨 Lỗi: {str(e)}")
