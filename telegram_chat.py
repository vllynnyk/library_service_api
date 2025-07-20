import os

from django.contrib.sites import requests
from rest_framework.response import Response
from dotenv import load_dotenv

from borrowings.models import Borrowing

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_message_into_group(borrowing: Borrowing, action: str) -> None:
    text = ""
    if action == "create":
        text = f"📚 New borrowing:\n• Book: {borrowing.book.title}\n• User: {borrowing.user.email}"
    elif action == "return":
        text = f"✅ Book returned:\n• Book: {borrowing.book.title}\n• User: {borrowing.user.email}"

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[Telegram Error] {e}")

