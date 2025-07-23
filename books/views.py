from drf_spectacular.utils import extend_schema
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

    @extend_schema(
        description="Retrieve a list of all books. Only ID, title, and author are shown. "
                    "You can optionally filter by title or author using search.",
        responses=BookListSerializer,
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Retrieve detailed information about a specific book by ID.",
        responses=BookSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
