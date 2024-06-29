# transaction.py

from django.db import models
from django.contrib.auth.models import User
from .models import Service  # Adjust the import based on your app structure

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    promo_code = models.CharField(max_length=50, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=50)
    provider_order_id = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100)
    signature_id = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.provider_order_id} by {self.user.username}"
