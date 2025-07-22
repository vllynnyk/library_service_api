import stripe

from django.urls import reverse
from rest_framework.request import Request

from borrowings.models import Borrowing
from payments.models import Payment

def create_stripe_payment(request: Request, borrowing: Borrowing) -> Payment:
    price = borrowing.calculate_total_price()

    payment = Payment.objects.create(
        status=Payment.PaymentStatus.PENDING,
        type=Payment.PaymentType.PAYMENT,
        borrowing=borrowing,
        money_to_pay=price,
    )

    success_url = request.build_absolute_uri(
        reverse("payments:payments-success", kwargs={"pk": payment.id})
    )
    cancel_url = request.build_absolute_uri(
        reverse("payments:payments-cancel", kwargs={"pk": payment.id})
    )

    session = stripe.checkout.Session.create(
        success_url=success_url,
        cancel_url=cancel_url,
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"{borrowing.book.title} borrowing"
                    },
                    "unit_amount": int(price * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
    )

    payment.session_url = session.url
    payment.session_id = session.id
    payment.save()

    return payment
