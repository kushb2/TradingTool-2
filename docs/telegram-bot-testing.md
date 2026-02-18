# Telegram Bot Test Guide (Beginner Friendly)

This guide helps you confirm your Telegram bot is working end-to-end.

## 1. Prerequisites

Run these once in project root:

```bash
poetry install
```

Set your bot token (replace with your real token):

```bash
export TELEGRAM_BOT_TOKEN="<bot_id>:<secret_from_botfather>"
```
chat_id=974882412
## 2. Start listener (Terminal 1)

```bash
poetry run python -m src.presentation.cli.telegram_cli listen --download-dir data/telegram_downloads
```

Expected startup log:

```text
Listening for incoming messages. Download dir: data/telegram_downloads
```

## 3. Send first message from phone

1. Open Telegram on your phone.
2. Open your bot chat.
3. Send `hello`.

Expected in Terminal 1:

```text
update_id=... chat_id=... message_id=... utc=...
text=hello
```

Save this `chat_id` value. You need it for sending messages from code.

## 4. Send message from code (Terminal 2)

Open a second terminal and run:

```bash
poetry run python -m src.presentation.cli.telegram_cli send --chat-id <your_chat_id> --text "Bot send test"
```

Expected:

```text
Sent message_id=... to chat_id=<your_chat_id>
```

You should receive `Bot send test` on your phone.

## 5. Test receiving screenshot/image

From phone, send:
- a screenshot, or
- any image as a normal photo.

Expected in Terminal 1:

```text
photo_saved=data/telegram_downloads/photo_<message_id>.jpg
```

## 6. Test receiving Excel/document

From phone:
1. Tap attachment icon.
2. Choose **File** (not Photo mode).
3. Send `.xlsx`, `.csv`, `.pdf`, or any document.

Expected in Terminal 1:

```text
document_saved=data/telegram_downloads/<message_id>_<original_filename>
```

## 7. Quick pass checklist

Bot is working if all are true:
- You can receive text in Terminal listener.
- You can send text from code to phone.
- Photos are saved to `data/telegram_downloads/`.
- Documents (Excel/files) are saved to `data/telegram_downloads/`.

## 8. Common issues

`Missing Telegram bot token`:
- You did not export `TELEGRAM_BOT_TOKEN`.

`Unauthorized` or `401`:
- Token is wrong or expired. Regenerate token in BotFather.

No updates appear in listener:
- Ensure you are messaging the correct bot.
- Start chat with bot and send `/start`.

`ModuleNotFoundError: src`:
- Run command from project root directory.

## 9. Stop listener

In Terminal 1, press:

```text
Ctrl + C
```
