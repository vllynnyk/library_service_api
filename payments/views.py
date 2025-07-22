import os

import stripe
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from dotenv import load_dotenv

from payments.models import Payment
from payments.serializers import PaymentListSerializer, PaymentSerializer
from permissions import IsAdminOrOwnerPermission

load_dotenv()


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

    @action(detail=True)
    def success(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.status != Payment.Status.PAID:
            stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
            session = stripe.checkout.Session.retrieve(instance.session_id)
            if session.payment_status == "paid":
                instance.status = Payment.Status.PAID
                instance.save()

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True)
    def cancel(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response({"detail": "Payment was canceled or failed."}, status=status.HTTP_200_OK)
