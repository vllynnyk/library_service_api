from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.utils import timezone

from borrowings.filters import BorrowingFilter
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingDetailSerializer
from telegram_chat import send_message_into_group

class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user").all()
    permission_classes = [IsAuthenticated]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = BorrowingFilter

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(user=user)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        return BorrowingSerializer

    def perform_create(self, serializer):
        borrowing = serializer.save(user=self.request.user)
        book = borrowing.book

        if book.inventory <= 0:
            raise serializers.ValidationError("This book is not available.")

        book.inventory -= 1
        book.save()
        send_message_into_group(borrowing, "create")

    @action(detail=True, methods=["POST"])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date:
            return Response({"detail": "Book already returned."},
                            status=status.HTTP_400_BAD_REQUEST)

        borrowing.actual_return_date = timezone.now()
        borrowing.save()

        book = borrowing.book
        book.inventory += 1
        book.save()
        send_message_into_group(borrowing, "return")

        return Response(BorrowingSerializer(borrowing).data)
