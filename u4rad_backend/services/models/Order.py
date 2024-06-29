from django.db import models
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _
from .constants import PaymentStatus
from django.contrib.auth.models import User


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    name = CharField(_("Customer Name"), max_length=254, blank=False, null=False)
    amount = models.FloatField(_("Amount"), null=False, blank=False)
    status = CharField(_("Payment Status"),default=PaymentStatus.PENDING, max_length=254, blank=False, null=False,)
    provider_order_id = models.CharField(_("Order ID"), max_length=40, null=False, blank=False)
    payment_id = models.CharField(_("Payment ID"), max_length=36, null=False, blank=False)
    signature_id = models.CharField(_("Signature ID"), max_length=128, null=False, blank=False)
    order_date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.id}-{self.name}-{self.status} on {self.order_date}"