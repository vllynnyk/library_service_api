from django.db import models
from rest_framework.exceptions import ValidationError

from books.models import Book
from library_service import settings


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="borrowings")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}: {str(self.borrow_date)}"

    @staticmethod
    def validate_book_availability(book: Book) -> None:
        if book.inventory < 1:
            raise ValidationError(f"The library does not have this book {book.title}")

    def clean(self):
        Borrowing.validate_book_availability(self.book)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def calculate_total_price(self):
        days = (self.expected_return_date - self.borrow_date).days
        return days * self.book.daily_fee
