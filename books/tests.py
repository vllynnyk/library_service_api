from django.test import TestCase
from rest_framework.reverse import reverse

from books.models import Book
from books.serializers import BookSerializer, BookListSerializer

BOOKS_URL = reverse("books:book-list")

class BookTest(TestCase):
    def setUp(self):
        self.book_1 = Book.objects.create(
            title="First Book",
            author="Jack Jonson",
            cover="Hard",
            inventory= 1000,
            daily_fee=20.00
        )
        self.book_2 = Book.objects.create(
            title="Second Book",
            author="Jack Jonson",
            cover="Hard",
            inventory= 1000,
            daily_fee=10.00
        )
        self.book_3 = Book.objects.create(
            title="Third Book",
            author="Jonny Lester",
            cover="Hard",
            inventory= 1000,
            daily_fee=9.99
        )

    def test_book_list(self):
        response = self.client.get(BOOKS_URL)
        book = Book.objects.all()
        serializer = BookListSerializer(book, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

    def test_book_detail(self):
        url = reverse("books:book-detail", kwargs={"pk": self.book_1.pk})
        response = self.client.get(url)
        serializer = BookSerializer(Book.objects.get(pk=self.book_1.pk))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.data["id"], self.book_1.pk)

    def test_book_search_by_title(self):
        response = self.client.get(f"{BOOKS_URL}?search=firs")
        expected_book = Book.objects.filter(title__icontains="firs")
        serializer = BookListSerializer(expected_book, many=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)
        titles = [book["title"] for book in response.data]
        self.assertIn(self.book_1.title, titles)
        self.assertNotIn(self.book_2.title, titles)
        self.assertNotIn(self.book_3.title, titles)

    def test_book_search_by_author(self):
        response = self.client.get(f"{BOOKS_URL}?search=lester")
        expected_book = Book.objects.filter(author__icontains="lester")
        serializer = BookListSerializer(expected_book, many=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, serializer.data)

        authors = [book["author"] for book in response.data]
        self.assertNotIn(self.book_1.author, authors)
        self.assertNotIn(self.book_2.author, authors)
        self.assertIn(self.book_3.author, authors)
