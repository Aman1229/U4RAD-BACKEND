from django.shortcuts import render, get_object_or_404, redirect
from .models.models import Service, ServiceRate
from .models.profile import Profile
from .models.CartItem import Cart
from .models.CartValue import CartValue
from .models.OrderHistory import OrderHistory
from .forms import ServiceForm, ServiceRateForm
from django.contrib.auth import login as ContribLogin
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as ContribLogout
import json
from .forms import ProfileForm
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import messages
import logging
from django.conf import settings
import razorpay
from .models.Order import Order
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from django.core.serializers import serialize
from django.forms.models import model_to_dict
import openpyxl
from io import BytesIO
from django.views.decorators.http import require_POST
from datetime import timedelta


def login(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST.get('password')
        new_password = request.POST.get('new_password')

        if User.objects.filter(username=phone).exists():
            # Existing user
            if password:  # Password should be provided for existing users
                user = authenticate(request, username=phone, password=password)
                if user is not None:
                    ContribLogin(request, user)
                    group = user.groups.values_list('name', flat=True).first()
                    if group == 'coordinator':
                        return redirect('service_list')
                    else:
                        return redirect('quality')
                else:
                    return render(request, 'services/login.html', {'error': 'Invalid login credentials'})
            else:
                return render(request, 'services/login.html', {'error': 'Password is required for existing users'})
        else:
            # New user
            if new_password:
                new_user = User.objects.create_user(username=phone, password=new_password)
                ContribLogin(request, new_user)
                return redirect('quality')
            else:
                return render(request, 'services/login.html', {'error': 'Please provide a new password to create an account'})

    return render(request, 'services/login.html')

def logout(request):
    ContribLogout(request)
    # return redirect('login')
    return redirect(settings.LOGOUT_REDIRECT_URL)

############################## RAZORPAY ###################################

def home(request):
    return render(request, "services/index.html")

@login_required
def quality(request):
    return render(request, "services/quality.html")    

def update_payment_status(request):
    if request.method == "POST":
        data = json.loads(request.body)
        print(data)
        order = Order.objects.get(provider_order_id=data['order_id'])
        order.payment_id = data['payment_id']
        order.signature_id = data['signature']
        order.status = data['status']
        order.save()
        return HttpResponse(status=200)


@csrf_protect
def generate_order(request):
    if request.method == "POST":
        data = json.loads(request.body)
        profile = Profile.objects.get(user=request.user)
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Create Razorpay order
        try:
            razorpay_order = client.order.create(
                {"amount": int(data['grand_total']) * 100, "currency": "INR", "payment_capture": "1"}
            )
        except razorpay.errors.BadRequestError as e:
            return render(request, "services/error.html", {"error": "Failed to create Razorpay order. Authentication failed."})

        # Create Order in your database
        order = Order.objects.create(
            name=profile.organization, amount=data['grand_total'], provider_order_id=razorpay_order["id"], user=request.user
        )
        order.save()

        return JsonResponse({'message': 'RZP Order generated successfully', 'order_id': order.provider_order_id, 'amount': int(data['grand_total']) * 100, 'key': settings.RAZORPAY_KEY_ID, 'user': { 'name': profile.organization, 'email': profile.email, 'contact': profile.user.username }})


        # return render(
        #     request,
        #     "services/payment.html",
        #     {
        #         "callback_url": request.build_absolute_uri("/razorpay/callback/"),
        #         "razorpay_key": settings.RAZORPAY_KEY_ID,
        #         "order": order,
        #     },
        # )

    return render(request, "services/payment.html")

############################################################################

@login_required
def user_dashboard(request):
    if request.user.is_authenticated:
        cart_items = Cart.objects.filter(user=request.user)
        cart_value = CartValue.objects.filter(user=request.user).first()
        orders = Order.objects.filter(user=request.user)
        context = {
            'cart_items': cart_items,
            'cart_value': cart_value,
            'orders': orders
        }
        return render(request, 'services/user_dashboard.html', context)
    else:
        return redirect('login')  # Redirect to login page if user is not authenticated
    


def download_invoice(request):
    if not request.user.is_authenticated:
        return redirect('login')

    # Get the last order for the current user
    last_order = Order.objects.filter(user=request.user).order_by('-order_date').first()

    if not last_order:
        return HttpResponse("No orders found.", content_type='text/plain')

    # Calculate the time window for filtering order histories (±5 minutes)
    time_window_start = last_order.order_date - timedelta(minutes=5)
    time_window_end = last_order.order_date + timedelta(minutes=5)

    # Get all order histories for the user within the time window
    last_order_histories = OrderHistory.objects.filter(
        user=request.user,
        order_date__range=(time_window_start, time_window_end)
    )

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Invoice"

    # Add order histories to the sheet
    if last_order_histories.exists():
        sheet['A1'] = 'Order History'
        sheet.append(['Service Name', 'Quantity', 'Amount'])
        for history in last_order_histories:
            service_name = history.service_name
            quantity = history.quantity
            amount = history.amount
            sheet.append([service_name, quantity, amount])

    sheet.append([])  # Empty row

    # Add the last order details to the sheet
    if last_order:
        sheet.append(['Order'])
        sheet.append(['Order ID', 'Customer Name', 'Amount', 'Status', 'Payment ID', 'Signature ID'])
        provider_order_id = last_order.provider_order_id
        name = last_order.name
        amount = last_order.amount
        status = last_order.status
        payment_id = last_order.payment_id
        signature_id = last_order.signature_id
        sheet.append([provider_order_id, name, amount, status, payment_id, signature_id])

    # Save the workbook to a BytesIO object
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=invoice.xlsx'
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    response.write(buffer.read())
    return response

@login_required
def coordinator_dashboard(request):
    # Fetch all profiles and cart items
    profiles = Profile.objects.select_related('user').all()
    cart_items = Cart.objects.select_related('user', 'service').all()
    name = Order.objects.select_related('user').all()

    context = {
        'profiles': profiles,
        'cart_items': cart_items,
    }

    return render(request, 'services/coordinator_dashboard.html', context)

@require_POST
def update_casecount(request, cart_item_id):
    cart_item = get_object_or_404(Cart, pk=cart_item_id)
    casecount = request.POST.get('casecount')
    cart_item.casecount = casecount
    cart_item.save()
    return redirect('coordinator_dashboard')


def update_profile(request):
    user_profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()  # Redirect to payment success after updating the profile
            return JsonResponse({'success': True})  # Return success JSON response
    else:
        form = ProfileForm(instance=user_profile)

    return render(request, 'services/update_profile.html', {'form': form})


########################################### 26-06 ###############################################
@login_required
def save_cart_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user = request.user
            cart_items = data.get('cart_items', [])
            promo_code = data.get('promo_code', '')
            total_amount = data.get('total_amount', 0)
            discount = data.get('discount', 0)
            grand_total = data.get('grand_total', 0)
            cart_value, created = CartValue.objects.get_or_create(user=user)
            if not created:
                # Append the new values to the existing ones
                cart_value.total_amount += total_amount
                cart_value.discount += discount
                cart_value.grand_total += grand_total
            else:
                # If it's a new CartValue instance, set the values
                cart_value.total_amount = total_amount
                cart_value.discount = discount
                cart_value.grand_total = grand_total
            cart_value.promo_code = promo_code
            cart_value.save()

            # Process each cart item
            for item in cart_items:
                quantity = item.get('quantity')
                amount = item.get('amount')
                service_name = item.get('service_name')

                # Ensure all required fields are present
                if not all([quantity, amount, service_name]):
                    return JsonResponse({'error': 'Missing fields in cart item'}, status=400)

                try:
                    # Retrieve the Service instance using service_name
                    service = Service.objects.get(service_name=service_name)
                except Service.DoesNotExist:
                    return JsonResponse({'error': f'Service "{service_name}" not found'}, status=404)

                # Save the order to OrderHistory
                OrderHistory.objects.create(
                    user=user,
                    service_name=service_name,
                    quantity=quantity,
                    amount=amount
                )

                # Check if a cart with the same user and service already exists
                cart_instance, created = Cart.objects.get_or_create(user=user, service=service)

                # If a cart with the same user and service already exists, update its fields
                if not created:
                    cart_instance.quantity += quantity
                    cart_instance.amount += amount
                else:
                    # If it doesn't exist, create a new cart instance
                    cart_instance.quantity = quantity
                    cart_instance.amount = amount
                cart_instance.save()

            return JsonResponse({'message': 'Cart data saved successfully', 'cart': cart_value.pk}, status=201)
        except Service.DoesNotExist:
            return JsonResponse({'error': 'Service not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
#################################################################################################


def payment_success(request):
    return render(request, 'services/payment_success.html')





def check_profile_completion(request):
    user = request.user
    if hasattr(user, 'profile'):
        user_profile = user.profile
        print("User Email:", user_profile.email)
        print("User Address:", user_profile.address)
        print("User Organization:", user_profile.organization)
        
        profile_complete = all([
            user_profile.email, 
            user_profile.address, 
            user_profile.organization
        ])
        print("Profile Complete:", profile_complete)
        
        return JsonResponse({"profile_complete": profile_complete})
    else:
        print("User profile does not exist.")
        return JsonResponse({"profile_complete": False, "message": "User profile does not exist."})
    




@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)





def checkout(request):
    try:
        user = User.objects.filter(username=request.user.username).first()
        
        if not user:
            return redirect('update_profile')

        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user)

        if not user.email or not user.profile.address or not user.profile.organization:
            return redirect('update_profile')

        return redirect('payment_success')

    except Exception as e:
        logging.exception("An error occurred during checkout:")
        return render(request, 'error.html', {'error': str(e)})
    



def check_user_exists(request):
    phone = request.GET.get('phone')
    exists = User.objects.filter(username=phone).exists()
    return JsonResponse({'exists': exists})




def convert_decimal(value):
    return int(value)



@login_required
def calculate_amount(request):
    services = Service.objects.filter(is_active=True).prefetch_related('rates')
    services_with_rates = []

    for service in services:
        rates = list(service.rates.values('min_quantity', 'max_quantity', 'rate'))
        for rate in rates:
            rate['rate'] = convert_decimal(rate['rate'])
        services_with_rates.append({
            'id': service.id,
            'service_name': service.service_name,
            'rates_json': json.dumps(rates),
            'rates': rates,
        })

    return render(request, 'services/calculate_amount.html', {'services': services_with_rates})





def cart(request):
    services = Service.objects.filter(is_active=True).prefetch_related('rates')
    services_with_rates = []

    for service in services:
        rates = list(service.rates.values('min_quantity', 'max_quantity', 'rate'))
        for rate in rates:
            rate['rate'] = convert_decimal(rate['rate'])
        services_with_rates.append({
            'id': service.id,
            'service_name': service.service_name,
            'rates_json': json.dumps(rates)
        })
    return render(request, 'services/cart.html', {'services': services_with_rates})




def home_redirect(request):
    return render(request, 'services/base_generic.html')




def service_list(request):
    services = Service.objects.all()
    return render(request, 'services/service_list.html', {'services': services})




@login_required
def service_create(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.added_by = request.user
            service.modified_by = request.user
            service.save()
            return redirect('service_list')
    else:
        form = ServiceForm()
    return render(request, 'services/service_form.html', {'form': form})





def service_update(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('service_list')
    else:
        form = ServiceForm(instance=service)
    return render(request, 'services/service_form.html', {'form': form})





def service_delete(request, pk):
    service = get_object_or_404(Service, pk=pk)
    if request.method == 'POST':
        service.delete()
        return redirect('service_list')
    return render(request, 'services/service_confirm_delete.html', {'service': service})





def service_rate_list(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    rates = service.rates.all()
    return render(request, 'services/service_rate_list.html', {'service': service, 'rates': rates})





def service_rate_create(request, service_id):
    service = get_object_or_404(Service, pk=service_id)
    if request.method == 'POST':
        form = ServiceRateForm(request.POST)
        if form.is_valid():
            rate = form.save(commit=False)
            rate.service = service
            rate.save()
            return redirect('service_rate_list', service_id=service_id)
    else:
        form = ServiceRateForm()
    return render(request, 'services/service_rate_form.html', {'form': form, 'service': service})





def service_rate_update(request, service_id, pk):
    rate = get_object_or_404(ServiceRate, service_id=service_id, pk=pk)
    if request.method == 'POST':
        form = ServiceRateForm(request.POST, instance=rate)
        if form.is_valid():
            form.save()
            return redirect('service_rate_list', service_id=service_id)
    else:
        form = ServiceRateForm(instance=rate)
    return render(request, 'services/service_rate_form.html', {'form': form, 'service': rate.service})





def service_rate_delete(request, service_id, pk):
    rate = get_object_or_404(ServiceRate, service_id=service_id, pk=pk)
    if request.method == 'POST':
        rate.delete()
        return redirect('service_rate_list', service_id=service_id)
    return render(request, 'services/service_rate_confirm_delete.html', {'rate': rate})