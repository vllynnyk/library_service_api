import uuid

from django.db import models

from borrowings.models import Borrowing

class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = "Pending"
        PAID = "Paid"
    class PaymentType(models.TextChoices):
        PAYMENT = "Payment"
        FINE = "Fine"
    status = models.CharField(max_length=10, choices=PaymentStatus.choices)
    type = models.CharField(max_length=10, choices=PaymentType.choices)
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE, related_name="payments")
    session_url = models.URLField()
    session_id = models.CharField(max_length=55)
    money_to_pay = models.DecimalField(decimal_places=2, max_digits=10)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"{self.type} {self.status}"
