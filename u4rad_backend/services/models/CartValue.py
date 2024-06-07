from django.db import models
from django.contrib.auth.models import User

class CartValue(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    promo_code = models.CharField(max_length=100, blank=True, null=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cart Item: {self.user} (Created at: {self.created_at})"