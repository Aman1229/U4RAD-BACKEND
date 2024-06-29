from django.contrib import admin
from .models.models import Service, ServiceRate
from .models.profile import Profile
from .models.CartItem import Cart
from .models.CartValue import CartValue
from .models.Order import Order
from .models.OrderHistory import OrderHistory

class ServiceRateInline(admin.TabularInline):
    model = ServiceRate
    extra = 1

class ServiceAdmin(admin.ModelAdmin):
    list_display = ('service_name', 'is_active', 'added_date', 'modified_date')
    inlines = [ServiceRateInline]
    readonly_fields = ('added_date', 'modified_date')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.added_by = request.user
        obj.modified_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Service, ServiceAdmin)
admin.site.register(Profile)
admin.site.register(Cart)
admin.site.register(CartValue)
admin.site.register(Order)
admin.site.register(OrderHistory)