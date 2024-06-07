from django.db import models
from django.contrib.auth.models import User

class Service(models.Model):
    service_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    added_date = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(User, related_name='services_added', on_delete=models.CASCADE)
    modified_date = models.DateTimeField(auto_now=True)
    modified_by = models.ForeignKey(User, related_name='services_modified', on_delete=models.CASCADE)

    def __str__(self):
        return self.service_name

class ServiceRate(models.Model):
    service = models.ForeignKey(Service, related_name='rates', on_delete=models.CASCADE)
    min_quantity = models.IntegerField()
    max_quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.service.service_name} ({self.min_quantity}-{self.max_quantity})"
