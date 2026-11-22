import json
import os
import time
import urllib.parse
import urllib.request

BOT_TOKEN = os.environ["BOT_TOKEN"]
OWNER_ID = int(os.environ["OWNER_ID"])
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def api_call(method: str, data: dict | None = None) -> dict:
    url = f"{API_URL}/{method}"
    if data is not None:
        encoded = urllib.parse.urlencode(data).encode("utf-8")
        req = urllib.request.Request(url, data=encoded)
    else:
        req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=35) as resp:
        return json.loads(resp.read().decode("utf-8"))


def send_message(chat_id: int | str, text: str, parse_mode: str | None = None):
    payload = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode
    return api_call("sendMessage", payload)


def copy_message(chat_id: int | str, from_chat_id: int | str, message_id: int):
    return api_call(
        "copyMessage",
        {
            "chat_id": chat_id,
            "from_chat_id": from_chat_id,
            "message_id": message_id,
        },
    )


def main():
    offset = 0
    print("Бот запущен...")
    while True:
        try:
            res = api_call("getUpdates", {"offset": offset, "timeout": 25})
            for upd in res.get("result", []):
                offset = upd["update_id"] + 1
                msg = upd.get("message")
                if not msg:
                    continue

                from_user = msg.get("from", {})
                user_id = from_user.get("id")
                text = msg.get("text", "")

                if text == "/start":
                    send_message(
                        user_id,
                        "Здравствуйте! Напишите ваше сообщение здесь — я передам его владельцу.",
                    )
                    continue

                if user_id == OWNER_ID:
                    send_message(
                        user_id,
                        "Вы владелец бота. Входящие сообщения от пользователей приходят сюда автоматически.",
                    )
                    continue

                full_name = " ".join(
                    part for part in [from_user.get("first_name"), from_user.get("last_name")] if part
                ) or "Без имени"
                username = f"@{from_user['username']}" if from_user.get("username") else "нет username"

                header = (
                    f"📩 <b>Новое сообщение от пользователя:</b>\n"
                    f"Имя: {full_name}\n"
                    f"Username: {username}\n"
                    f"ID: <code>{user_id}</code>\n"
                    f"───────────────"
                )
                send_message(OWNER_ID, header, parse_mode="HTML")
                copy_message(OWNER_ID, msg["chat"]["id"], msg["message_id"])
                send_message(user_id, "Сообщение отправлено!")
        except Exception as e:
            print("Ошибка цикла:", e)
            time.sleep(3)


if __name__ == "__main__":
    main()
          
