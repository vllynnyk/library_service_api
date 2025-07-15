from rest_framework import viewsets, filters

from books.serializers import BookSerializer, BookListSerializer
from books.models import Book


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    filter_backends = (filters.SearchFilter,)
    search_fields = ("title", "author")

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer
