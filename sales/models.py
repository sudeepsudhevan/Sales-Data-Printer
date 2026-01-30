from django.db import models

class MoneyReceived(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Money Received")

    is_settled = models.BooleanField(default=False, verbose_name="Settled")

    def __str__(self):
        return f"{self.date} - {self.amount}"

class ItemSold(models.Model):
    date = models.DateField()
    weight = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Weight (kg)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price (per unit)")
    total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total (Rupees)", editable=False)
    is_closed = models.BooleanField(default=False, verbose_name="Closed")

    def save(self, *args, **kwargs):
        self.total = self.weight * self.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.date} - {self.total}"
