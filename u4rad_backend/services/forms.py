from django import forms
from .models.models import Service, ServiceRate
from .models.profile import Profile

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['service_name', 'is_active']

class ServiceRateForm(forms.ModelForm):
    class Meta:
        model = ServiceRate
        fields = ['service', 'min_quantity', 'max_quantity', 'rate']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['email', 'address', 'organization']          