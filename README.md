# Telegram Chat ID Bot

Bot Telegram nhỏ viết bằng Python, dùng để trả về `chat_id` của cuộc trò chuyện hiện tại. ID này thường cần khi cấu hình hệ thống gửi cảnh báo, báo cáo hoặc thông báo tự động qua Telegram.

## Chức năng

- Nhận lệnh `/getid`.
- Trả về ID của private chat, group hoặc channel nơi bot nhận message.
- Đọc bot token từ biến môi trường thay vì hard-code.
- Có `Dockerfile` và cấu hình `fly.toml` để chạy dạng container.

## Cấu trúc

```text
bot.py            # Entry point và command handler
requirements.txt  # Dependency Python
Dockerfile        # Image chạy bot
fly.toml          # Cấu hình Fly.io
```

## Tạo bot

1. Mở cuộc trò chuyện với **@BotFather**.
2. Chạy `/newbot` và làm theo hướng dẫn.
3. Lưu token ở nơi an toàn; không commit token lên GitHub.
4. Nếu dùng trong group, thêm bot vào group và cấp quyền tối thiểu cần thiết.

## Chạy cục bộ

Yêu cầu Python 3.10+:

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Thiết lập token:

```powershell
$env:BOT_TOKEN="your_bot_token"
python bot.py
```

Sau khi bot online, gửi `/getid` trong cuộc trò chuyện cần lấy ID.

## Chạy bằng Docker

```bash
docker build -t telegram-chat-id-bot .
docker run --rm -e BOT_TOKEN=your_bot_token telegram-chat-id-bot
```

## Triển khai Fly.io

1. Cài và đăng nhập Fly CLI.
2. Kiểm tra tên app/region trong `fly.toml`.
3. Lưu token bằng secret:

```bash
fly secrets set BOT_TOKEN=your_bot_token
fly deploy
fly logs
```

Không đặt token trực tiếp trong `fly.toml`.

## Cách hiểu `chat_id`

- Private chat thường là số dương.
- Group/supergroup thường có ID âm.
- ID không phải username và không nên ép sang kiểu số 32-bit.
- Bot chỉ có thể nhận lệnh ở nơi nó được thêm và được phép đọc message phù hợp.

## Xử lý sự cố

- Bot không phản hồi: kiểm tra token, log và xem đã chạy đúng process chưa.
- Group không phản hồi: thêm bot, thử lệnh `/getid@TenBot`, kiểm tra privacy mode.
- Deploy dừng: kiểm tra health/restart policy và biến `BOT_TOKEN`.
- `Conflict: terminated by other getUpdates`: đang có hai instance polling cùng token; chỉ giữ một instance.

## Bảo mật và tối giản dependency

Token Telegram cho phép điều khiển bot; nếu bị lộ hãy revoke ngay tại BotFather. Repository chỉ cần thư viện Telegram và dependency trực tiếp của nó. Nếu `requirements.txt` còn các gói phân tích dữ liệu/biểu đồ không được `bot.py` import, nên xóa để image nhỏ hơn và giảm bề mặt lỗ hổng.

## Hướng phát triển

- Thêm `/start` và hướng dẫn sử dụng.
- Giới hạn người dùng nếu bot chỉ phục vụ nội bộ.
- Thêm logging có cấu trúc và graceful shutdown.
- Pin version dependency và quét bảo mật container.
- Thêm test cho command handler.
