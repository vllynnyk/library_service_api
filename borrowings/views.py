from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.utils import timezone

from borrowings.filters import BorrowingFilter
from borrowings.models import Borrowing
from borrowings.serializers import BorrowingSerializer, BorrowingListSerializer, BorrowingDetailSerializer
from permissions import IsAdminOrOwnerPermission
from telegram_chat import send_message_into_group
from payments.stripe_session import create_stripe_payment

class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user").all()
    permission_classes = [IsAuthenticated, IsAdminOrOwnerPermission]
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

    @extend_schema(
        description="Create a new borrowing. Requires a valid book with positive inventory. "
                    "Optionally filter by created.",
        responses=BorrowingSerializer,
    )
    def perform_create(self, serializer):
        with transaction.atomic():
            borrowing = serializer.save(user=self.request.user)
            book = borrowing.book

            if book.inventory <= 0:
                raise serializers.ValidationError("This book is not available.")

            book.inventory -= 1
            book.save()
            create_stripe_payment(self.request, borrowing)
            send_message_into_group(borrowing, "create")

    @extend_schema(
        description="Mark the borrowing as returned. Increases book inventory and sets actual_return_date. "
                    "Fails if already returned.",
        responses=BorrowingSerializer,
    )
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

    @extend_schema(
        description="Retrieve a list of all borrowings. Only ID, borrowing_date, and book_title are shown. "
                    "You can optionally custom filter by is_active.",
        responses=BorrowingListSerializer,
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Retrieve detailed information about a specific borrowing by ID.",
        responses=BorrowingDetailSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
