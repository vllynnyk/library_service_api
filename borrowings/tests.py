from datetime import datetime, date

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Book
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer

BORROWING_URL = reverse("borrowings:borrowing-list")

class BorrowingTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_1 = get_user_model().objects.create_user(
            email="first@user.com",
            password="1234pass",
            first_name="First",
            last_name="User",
        )
        cls.user_2 = get_user_model().objects.create_user(
            email="second@user.com",
            password="1234pass",
            first_name="Second",
            last_name="User",
        )
        cls.admin = get_user_model().objects.create_superuser(
            email="test@admin.com",
            password="1234pass",
            first_name="Super",
            last_name="User",
        )
        cls.book_1 = Book.objects.create(
            title="Black Day",
            author = "Jack Smith",
            cover = "Hard",
            inventory = 0,
            daily_fee = 12.99
        )
        cls.book_2 = Book.objects.create(
            title="White Day",
            author="Jack Smith",
            cover="Hard",
            inventory=100,
            daily_fee=12.99
        )
        cls.book_3 = Book.objects.create(
            title="Yellow Day",
            author="Jack Smith",
            cover="Hard",
            inventory=200,
            daily_fee=12.99
        )
        cls.borrow_1 = Borrowing.objects.create(
            book=cls.book_2,
            user=cls.user_2,
            borrow_date=datetime.today(),
            expected_return_date=date(2025, 8, 12)
        )
        cls.borrow_2 = Borrowing.objects.create(
            book=cls.book_3,
            user=cls.user_1,
            borrow_date=datetime.today(),
            expected_return_date=date(2025, 8, 12)
        )
        cls.borrow_3 = Borrowing.objects.create(
            book=cls.book_2,
            user=cls.user_1,
            borrow_date=datetime.today(),
            expected_return_date=date(2025, 8, 12),
        )
        cls.borrow_4 = Borrowing.objects.create(
            book=cls.book_2,
            user=cls.user_1,
            borrow_date=datetime.today(),
            expected_return_date=date(2025, 8, 12),
            actual_return_date=datetime.today()
        )

class UnauthenticatedBorrowingApiTests(BorrowingTests):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(BORROWING_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
