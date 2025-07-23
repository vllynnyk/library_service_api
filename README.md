# Library Service API

A RESTful API for managing a library system where users can borrow books, make payments via Stripe, and receive notifications via Telegram.

---

## Overview

This project is built with Django and Django REST Framework.

Key features:
- User registration and authentication
- Book management and browsing
- Borrowing and returning books
- Stripe Checkout integration for payments
- Telegram bot notifications for borrowing and returns

---

## Technologies Used

- Python 3.11+
- Django 5.2
- Django REST Framework
- Stripe API
- Telegram Bot API
- SQLite (default database)
- python-dotenv for environment variables

---

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/vllynnyk/library_service_api.git
   cd library_service_api
   ```
   
2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate      # Linux/macOS
    venv\Scripts\activate         # Windows
    ```
   
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
   
4. Create a .env file based on .env.sample and fill in your environment variables:
    ```env
    SECRET_KEY=your_secret_key
    TELEGRAM_TOKEN=your_telegram_bot_token
    TELEGRAM_CHAT_ID=your_telegram_chat_id
    STRIPE_SECRET_KEY=your_stripe_secret_key
    ```

5. Apply database migrations:
    ```bash
    python manage.py migrate
    ```
   
6. Run the development server:
    ```bash 
    python manage.py runserver
    ```

## Running Tests

1. Run the test suite with:
    ```bash
    python manage.py test
    ```
    External service calls (Telegram, Stripe) are mocked in tests for isolation.
