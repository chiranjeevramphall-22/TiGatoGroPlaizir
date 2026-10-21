from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.urls import reverse
from .models import Cake, Profile, Order, CustomisationOption
from .forms import SignupForm, CakeForm, CustomisationOptionForm
from django.views.decorators.http import require_POST

# =====================================================
# PUBLIC PAGES
# =====================================================
def home(request):
    return render(request, 'bakery/home.html')

def our_cakes(request):
    cakes = Cake.objects.all()
    return render(request, 'bakery/our_cakes.html', {'cakes': cakes})

# =====================================================
# CAKE DETAIL VIEW
# Shows one cake + handles the standard order submission
# =====================================================
def cake_detail(request, cake_id):
    cake = get_object_or_404(Cake, pk=cake_id)
    
    # ---------- HANDLE ORDER SUBMISSION ----------
    if request.method == 'POST' and request.user.is_authenticated:
        # Get the form data
        size = request.POST.get('size', 'Small (6")')
        total_price = request.POST.get('total_price')
        payment_method = request.POST.get('payment_method', 'cod')
        payment_reference = request.POST.get('payment_reference', '').strip()
        fulfilment_method = request.POST.get('fulfilment_method', 'pickup') 
        
        # ---------- SERVER-SIDE VALIDATION ----------
        if payment_method in ['mcb_juice', 'bank_transfer'] and not payment_reference:
            messages.error(
                request, 
                "Please provide your payment reference code for MCB Juice or Bank Transfer."
            )
            return redirect('cake_detail', cake_id=cake.id)
        
        # Get the user's profile for delivery info
        try:
            profile = request.user.profile
            delivery_address = profile.delivery_address
            phone_number = profile.phone_number
        except Profile.DoesNotExist:
            delivery_address = ''
            phone_number = ''
        
        # Create the order in the database
        order = Order.objects.create(
            customer=request.user,
            cake=cake,
            size=size,
            total_price=total_price,
            payment_method=payment_method,
            payment_reference=payment_reference,
            fulfilment_method=fulfilment_method,  
            delivery_address=delivery_address,
            phone_number=phone_number,
            status='pending',
        )
        
        messages.success(
            request,
            f"🎉 Your order #{order.id} for '{cake.name}' has been placed! "
            f"We will confirm your payment and start baking soon."
        )
        
        return redirect('cake_detail', cake_id=cake.id)
    
    # ---------- SHOW THE PAGE ----------
    return render(request, 'bakery/cake_detail.html', {'cake': cake})

# =====================================================
# ABOUT US
# =====================================================
def about_us(request):
    return render(request, 'bakery/about_us.html')

# =====================================================
# AUTHENTICATION
# =====================================================
def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            from django.contrib.auth import login
            login(request, user)
            messages.success(request, f"Welcome to the family, {user.profile.full_name}! 🎉 Your account is ready.")
            return redirect('home')
    else:
        form = SignupForm()
    
    return render(request, 'bakery/signup.html', {'form': form})

# =====================================================
# CUSTOM LOGIN VIEW
# Handles both customers and admins.
# Shows a personalised welcome message.
# handles users who don't have a Profile yet (e.g. admins).
# =====================================================
class CustomLoginView(LoginView):
    template_name = 'bakery/login.html'
    
    def form_valid(self, form):
        user = form.get_user()
        
        # Check if the user has a profile. If yes, use full name.
        # If no (like an admin), fall back to the username.
        if hasattr(user, 'profile'):
            name = user.profile.full_name
        else:
            name = user.username
        
        messages.success(self.request, f"Welcome back, {name}! Ready to order? 🍰")
        return super().form_valid(form)

# =====================================================
# LOGOUT VIEW
# Logs the user out and sends them back to the home page
# with a friendly message.
# =====================================================
def custom_logout(request):
    logout(request)
    messages.info(request, "You have been logged out. See you soon! 👋")
    return redirect('home')
    

# # =====================================================
# CUSTOMISE VIEW
# Shows the customise page + handles custom order submission
# =====================================================
def customise(request):
    
    # ---------- HANDLE ORDER SUBMISSION ----------
    if request.method == 'POST' and request.user.is_authenticated:
        # Get the options the user selected
        custom_size = request.POST.get('custom_size', '')
        custom_flavour = request.POST.get('custom_flavour', '')
        custom_filling = request.POST.get('custom_filling', '')
        custom_frosting = request.POST.get('custom_frosting', '')
        custom_decorations = request.POST.get('custom_decorations', '')
        customer_notes = request.POST.get('customer_notes', '')

        # NEW: Get the optional event details
        cake_type = request.POST.get('cake_type', '')
        theme = request.POST.get('theme', '')
        colour_scheme = request.POST.get('colour_scheme', '')
        required_date = request.POST.get('required_date') or None  # empty string becomes None

        # Server-side validation confirms that submitted values are
        # still active options from the database.
        required_selections = {
            'size': custom_size,
            'flavour': custom_flavour,
            'filling': custom_filling,
            'frosting': custom_frosting,
        }
        selections_are_valid = all(
            value and CustomisationOption.objects.filter(
                category=category,
                name__iexact=value,
            ).exists()
            for category, value in required_selections.items()
        )

        decoration_names = [
            name.strip() for name in custom_decorations.split(',') if name.strip()
        ]
        decorations_are_valid = all(
            CustomisationOption.objects.filter(
                category='decoration',
                name__iexact=name,
            ).exists()
            for name in decoration_names
        )

        if not selections_are_valid or not decorations_are_valid:
            messages.error(
                request,
                "Please select valid size, flavour, filling and frosting options."
            )
            return redirect('customise')
        
        # Get the user's profile for delivery info
        try:
            profile = request.user.profile
            delivery_address = profile.delivery_address
            phone_number = profile.phone_number
        except Profile.DoesNotExist:
            delivery_address = ''
            phone_number = ''
        
        # Create the custom order in the database
        order = Order.objects.create(
            customer=request.user,
            cake=None,
            is_custom=True,
            custom_size=custom_size,
            custom_flavour=custom_flavour,
            custom_filling=custom_filling,
            custom_frosting=custom_frosting,
            custom_decorations=custom_decorations,
            customer_notes=customer_notes,
            total_price=0,
            payment_method='discuss',
            delivery_address=delivery_address,
            phone_number=phone_number,
            status='pending',
            # NEW: Save event details to the order
            cake_type=cake_type,
            theme=theme,
            colour_scheme=colour_scheme,
            required_date=required_date,
        )
        
        # Show success message
        messages.success(
            request,
            f"🎉 Your custom cake request #{order.id} has been submitted! "
            f"We will contact you shortly to confirm the details and price."
        )
        
        return redirect('customise')
    
    # ---------- SHOW DATABASE-DRIVEN OPTIONS ----------
    context = {
        'size_options': CustomisationOption.objects.filter(category='size'),
        'flavour_options': CustomisationOption.objects.filter(category='flavour'),
        'filling_options': CustomisationOption.objects.filter(category='filling'),
        'frosting_options': CustomisationOption.objects.filter(category='frosting'),
        'decoration_options': CustomisationOption.objects.filter(category='decoration'),
    }
    return render(request, 'bakery/customise.html', context)

# =====================================================
# ADMIN LOGIN VIEW
# Custom admin login — only staff accounts can log in.
# =====================================================

def admin_login(request):
    # If already logged in as staff, skip straight to dashboard
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    
    # If the form was submitted
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check the credentials
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff:
                # Valid staff account — log in and redirect
                login(request, user)
                messages.success(request, f"Welcome back, Admin {user.username}! 🔐")
                return redirect('admin_dashboard')
            else:
                # Valid user, but not staff
                messages.error(request, "This account does not have admin access.")
        else:
            # Invalid credentials
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'bakery/admin_login.html')

# =====================================================
# ADMIN: CUSTOMER ACCOUNTS PAGE
# Shows all registered customers (non-staff only).
# Only accessible by staff users.
# =====================================================

# Helper function: checks if a user is a staff member
def is_staff(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_staff, login_url='admin_login')
def admin_dashboard(request):
    # Redirect to the customers page as the default admin page
    return redirect('admin_customers')


@user_passes_test(is_staff, login_url='admin_login')
def admin_customers(request):
    # Fetch all users, but exclude staff accounts (so admins don't see themselves)
    customers = User.objects.filter(is_staff=False).order_by('-date_joined')
    
    context = {
        'customers': customers,
        'active_page': 'customers',   # Tells the sidebar which link is active
    }
    return render(request, 'bakery/admin_customers.html', context)

# =====================================================
# ADMIN: CAKE CATALOGUE PAGE
# Add, edit and remove cake designs, and switch
# availability on or off. Staff only.
# @k.d
# =====================================================
@user_passes_test(is_staff, login_url='admin_login')
def admin_catalogue(request):
    if request.method == 'POST':
        form = CakeForm(request.POST, request.FILES)
        if form.is_valid():
            cake = form.save()
            messages.success(request, f"\"{cake.name}\" was added to the catalogue.")
            return redirect('admin_catalogue')
    else:
        form = CakeForm()
 
    return render(request, 'bakery/admin_catalogue.html', {
        'form': form,
        'cakes': Cake.objects.order_by('id'),
        'active_page': 'catalogue',
    })
 
 
@user_passes_test(is_staff, login_url='admin_login')
def admin_cake_edit(request, cake_id):
    cake = get_object_or_404(Cake, pk=cake_id)
 
    if request.method == 'POST':
        form = CakeForm(request.POST, request.FILES, instance=cake)
        if form.is_valid():
            form.save()
            messages.success(request, f"\"{cake.name}\" was updated.")
            return redirect('admin_catalogue')
    else:
        form = CakeForm(instance=cake)
 
    return render(request, 'bakery/admin_catalogue.html', {
        'form': form,
        'cakes': Cake.objects.order_by('id'),
        'editing': cake,
        'active_page': 'catalogue',
    })
 
 
@require_POST
@user_passes_test(is_staff, login_url='admin_login')
def admin_cake_delete(request, cake_id):
    cake = get_object_or_404(Cake, pk=cake_id)
    name = cake.name
    cake.delete()   # Orders keep existing: Order.cake is SET_NULL
    messages.success(request, f"\"{name}\" was removed from the catalogue.")
    return redirect('admin_catalogue')


# =====================================================
# ADMIN: CUSTOMISATION OPTIONS PAGE
# Lets staff view, add and remove the sizes, flavours,
# fillings, frostings and decorations shown to customers.
# Every operation is protected by a staff permission check.
# =====================================================
@user_passes_test(is_staff, login_url='admin_login')
def admin_customisation_options(request):
    valid_categories = dict(CustomisationOption.CATEGORY_CHOICES)

    # GET uses the selected tab; POST uses the hidden category field.
    active_category = (
        request.POST.get('category')
        if request.method == 'POST'
        else request.GET.get('category', 'size')
    )
    if active_category not in valid_categories:
        active_category = 'size'

    if request.method == 'POST':
        form = CustomisationOptionForm(
            request.POST,
            category=active_category,
        )
        if form.is_valid():
            option = form.save()
            messages.success(request, f'"{option.name}" was added successfully.')
            return redirect(
                f"{reverse('admin_customisation_options')}?category={active_category}"
            )
    else:
        form = CustomisationOptionForm(category=active_category)

    context = {
        'form': form,
        'categories': CustomisationOption.CATEGORY_CHOICES,
        'active_category': active_category,
        'active_category_label': valid_categories[active_category],
        'options': CustomisationOption.objects.filter(category=active_category),
        'active_page': 'options',
    }
    return render(request, 'bakery/admin_customisation_options.html', context)


@require_POST
@user_passes_test(is_staff, login_url='admin_login')
def admin_customisation_option_delete(request, option_id):
    option = get_object_or_404(CustomisationOption, pk=option_id)
    active_category = option.category
    option_name = option.name
    option.delete()
    messages.success(request, f'"{option_name}" was removed successfully.')
    return redirect(
        f"{reverse('admin_customisation_options')}?category={active_category}"
    )

# =====================================================
# ADMIN: CUSTOM REQUESTS PAGE
# Shows all custom cake orders for the admin to review,
# set prices, and approve/reject.
# =====================================================
@user_passes_test(is_staff, login_url='admin_login')
def admin_custom_requests(request):
    # ---------- HANDLE THE APPROVE / REJECT BUTTON CLICK ----------
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        action = request.POST.get('action')
        price = request.POST.get('price')
        admin_notes = request.POST.get('admin_notes', '')
        
        # Find the specific order
        order = get_object_or_404(Order, id=order_id, is_custom=True)
        
        if action == 'approve' and price:
            order.total_price = price
            order.admin_notes = admin_notes
            order.status = 'confirmed'
            order.save()
            messages.success(request, f"Order #{order.id} has been approved with a price of Rs {price}.")
            
        elif action == 'reject':
            order.admin_notes = admin_notes
            order.status = 'cancelled'
            order.save()
            messages.error(request, f"Order #{order.id} has been rejected.")
            
        return redirect('admin_custom_requests')

    # ---------- SHOW THE PAGE ----------
    custom_orders = Order.objects.filter(is_custom=True).order_by('-created_at')
    
    context = {
        'custom_orders': custom_orders,
        'active_page': 'requests',
    }
    return render(request, 'bakery/admin_custom_requests.html', context)

# =====================================================
# ADMIN: CUSTOMER ORDERS PAGE
# Shows all standard cake orders (not custom).
# Allows the admin to update the status via buttons.
# =====================================================
@user_passes_test(is_staff, login_url='admin_login')
def admin_orders(request):
    
    # ---------- HANDLE STATUS UPDATE BUTTON CLICK ----------
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        
        # Find the specific order and update its status
        order = get_object_or_404(Order, id=order_id, is_custom=False)
        order.status = new_status
        order.save()
        
        messages.success(request, f"Order #{order.id} status updated to {order.get_status_display()}.")
        return redirect('admin_orders')

    # ---------- SHOW THE PAGE ----------
    # Get only standard orders (is_custom=False)
    orders = Order.objects.filter(is_custom=False).order_by('-created_at')
    
    context = {
        'orders': orders,
        'active_page': 'orders',
    }
    return render(request, 'bakery/admin_orders.html', context)

# =====================================================
# CUSTOMER PROFILE VIEW
# Shows the user's personal details and handles editing.
# =====================================================
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')
def my_profile(request):
    user = request.user
    
    # ---------- HANDLE EDIT PROFILE SUBMISSION ----------
    if request.method == 'POST':
        # Get the data from the form
        full_name = request.POST.get('full_name', '')
        email = request.POST.get('email', '')
        phone_number = request.POST.get('phone_number', '')
        delivery_address = request.POST.get('delivery_address', '')
        
        # Update the User model (Email)
        user.email = email
        user.save()
        
        # Update the Profile model
        profile = user.profile
        profile.full_name = full_name
        profile.phone_number = phone_number
        profile.delivery_address = delivery_address
        profile.save()
        
        messages.success(request, "Your profile has been updated successfully! ✅")
        return redirect('my_profile')

    # ---------- SHOW THE PAGE ----------
    # Count current orders
    current_orders_count = Order.objects.filter(
        customer=user, 
        status__in=['pending', 'confirmed', 'baking', 'ready']
    ).count()
    
    # Count history
    history_count = Order.objects.filter(
        customer=user, 
        status__in=['delivered', 'cancelled']
    ).count()
    
    context = {
        'active_page': 'profile',
        'current_orders_count': current_orders_count,
        'history_count': history_count,
    }
    return render(request, 'bakery/my_profile.html', context)