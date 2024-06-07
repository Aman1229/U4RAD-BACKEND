from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('', views.login, name='login'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('check_profile_completion/', views.check_profile_completion, name='check_profile_completion'),
    path('check_user_exists/', views.check_user_exists, name='check_user_exists'),
    path('services/', views.service_list, name='service_list'),
    path('services/add/', views.service_create, name='service_create'),
    path('services/<int:pk>/edit/', views.service_update, name='service_update'),
    path('services/<int:pk>/delete/', views.service_delete, name='service_delete'),
    path('services/<int:service_id>/rates/', views.service_rate_list, name='service_rate_list'),
    path('services/<int:service_id>/rates/add/', views.service_rate_create, name='service_rate_create'),
    path('services/<int:service_id>/rates/<int:pk>/edit/', views.service_rate_update, name='service_rate_update'),
    path('services/<int:service_id>/rates/<int:pk>/delete/', views.service_rate_delete, name='service_rate_delete'),
    path('calculate-amount/', views.calculate_amount, name='calculate_amount'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('save_cart_data/', views.save_cart_data, name='save_cart_data'),
    path('user_dashboard/', login_required(views.user_dashboard), name='user_dashboard'),
    path('logout/', views.logout, name='logout'),
    path("payment/", views.generate_order, name="generate_order"),
    path("home/", views.home, name="home"),
    path("payment/update-status/", views.update_payment_status, name='update_payment_status')
]
