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
            is_staff=True,
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


class AuthenticatedBorrowingApiTests(BorrowingTests):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.user_1)

    def test_borrowing_list(self):
        response = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.filter(user=self.user_1)
        serializer = BorrowingListSerializer(borrowings, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), serializer.data)

    def test_borrowing_create_decreases_inventory(self):
        payload = {
            "book": self.book_2.id,
            "expected_return_date": date(2025, 7, 22)
        }
        response = self.client.post(BORROWING_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book_2.refresh_from_db()
        self.assertEqual(self.book_2.inventory, 99)

    def test_borrowing_return_decreases_inventory(self):
        borrowing = self.borrow_3
        borrowing.book.inventory -= 1
        borrowing.book.save()
        previous_inventory = borrowing.book.inventory

        url = reverse("borrowings:borrowing-return-book", args=[borrowing.id])
        response = self.client.post(url)

        borrowing.refresh_from_db()
        borrowing.book.refresh_from_db()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(borrowing.actual_return_date)
        self.assertEqual(borrowing.book.inventory,    previous_inventory + 1)

    def test_return_book_already_returned(self):
        borrowing = self.borrow_4
        url = reverse("borrowings:borrowing-return-book", args=[borrowing.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()["detail"], "Book already returned.")


    def test_borrowing_validate_with_empty_inventory(self):
        payload = {
            "book": self.book_1.id,
            "expected_return_date": date(2025, 7, 22)
        }
        response = self.client.post(BORROWING_URL, payload)
        serializer = BorrowingSerializer(data=payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(serializer.is_valid())
        self.assertIn("book", serializer.errors)
        self.assertIn("Black Day", str(serializer.errors["book"]))

    def test_borrowing_filter_is_active(self):
        response = self.client.get(BORROWING_URL, {"is_active": "true"})
        borrowings = Borrowing.objects.filter(user=self.user_1, actual_return_date__isnull=True)
        serializer = BorrowingListSerializer(borrowings, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), serializer.data)

        returned_ids = [item["id"] for item in response.json()]
        self.assertNotIn(self.borrow_4.id, returned_ids)


class AdminBorrowingApiTests(BorrowingTests):
    def setUp(self):
        self.client = APIClient()
        self.client.force_authenticate(user=self.admin)

    def test_borrowing_list_admin(self):
        response = self.client.get(BORROWING_URL)
        borrowings = Borrowing.objects.all()
        serializer = BorrowingListSerializer(borrowings, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), serializer.data)

    def test_borrowing_filter_by_users(self):
        response = self.client.get(BORROWING_URL, {"user_id": self.user_2.id})
        borrowings = Borrowing.objects.filter(user=self.user_2)
        serializer = BorrowingListSerializer(borrowings, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), serializer.data)
