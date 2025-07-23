import stripe
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from payments.models import Payment
from payments.serializers import PaymentListSerializer, PaymentSerializer
from permissions import IsAdminOrOwnerPermission



class PaymentViewSet(mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    queryset = Payment.objects.select_related("borrowing").all()
    permission_classes = [IsAuthenticated, IsAdminOrOwnerPermission]

    def get_queryset(self):
        queryset = self.queryset
        user = self.request.user
        if not user.is_staff:
            queryset = queryset.filter(borrowing__user=user)
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        else:
            return PaymentSerializer

    @extend_schema(
        description="Mark the Payment status as paid.",
        responses=PaymentSerializer,
    )
    @action(detail=True, methods=["get"])
    def success(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status != Payment.PaymentStatus.PAID:
            session = stripe.checkout.Session.retrieve(instance.session_id)
            if session.payment_status == "paid":
                instance.status = Payment.PaymentStatus.PAID
                instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @extend_schema(
        description="The payment was canceled or failed.",
        responses=OpenApiResponse(
            description="Simple message indicating the cancellation or failure of the payment.",
            response=OpenApiTypes.OBJECT
        )
    )
    @action(detail=True, methods=["get"])
    def cancel(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({"detail": "Payment was canceled or failed."}, status=status.HTTP_200_OK)

    @extend_schema(
        description="Retrieve a list of all payments. Only ID and status are shown.",
        responses=PaymentListSerializer,
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        description="Retrieve detailed information about a specific payment by ID."
                    "",
        responses=PaymentSerializer,
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
