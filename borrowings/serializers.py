from rest_framework import serializers

from borrowings.models import Borrowing
from books.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ['id', 'borrow_date', 'expected_return_date', 'actual_return_date', 'book']

    def validate_book(self, book):
        Borrowing.validate_book_availability(book)
        return book


class BorrowingListSerializer(BorrowingSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    class Meta:
        model = Borrowing
        fields = ['id', 'borrow_date', 'book_title']

class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer(read_only=True)
    class Meta:
        model = Borrowing
        fields = ['id', 'borrow_date', 'expected_return_date', 'actual_return_date', 'book']
