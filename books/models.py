from django.db import models


class Book(models.Model):
    class CoverChoices(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=100)
    cover = models.CharField(max_length=5, choices=CoverChoices.choices)
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ("title",)

    def __str__(self):
        return (
            f"{self.title} | Author: {self.author} | "
            f"Inventory: {self.inventory} | Daily Fee: ${self.daily_fee}"
        )
