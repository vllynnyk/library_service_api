import requests

from borrowings.models import Borrowing
from library_service import settings


def send_message_into_group(borrowing: Borrowing, action: str) -> None:
    text = ""
    if action == "create":
        text = f"📚 New borrowing:\n• Book: {borrowing.book.title}\n• User: {borrowing.user.email}"
    elif action == "return":
        text = f"✅ Book returned:\n• Book: {borrowing.book.title}\n• User: {borrowing.user.email}"

    url = f"https://api.telegram.org/bot{settings.TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": settings.TELEGRAM_CHAT_ID, "text": text}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[Telegram Error] {e}")

