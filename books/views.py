from rest_framework import viewsets, filters
from rest_framework.permissions import IsAdminUser, AllowAny

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

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [IsAdminUser()]
        return [AllowAny()]
