# models.py

from django.contrib.auth.models import User
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=100, blank=True)
    organization = models.CharField(max_length=100, blank=True)
