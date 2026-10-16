from django.shortcuts import render, get_object_or_404
from .models import Cake, Profile, Order
from django.shortcuts import render, redirect
from .forms import SignupForm
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from django.shortcuts import redirect


def home(request):
    return render(request, 'bakery/home.html')

def our_cakes(request):
    cakes = Cake.objects.all()
    return render(request, 'bakery/our_cakes.html', {'cakes': cakes})

def cake_detail(request, cake_id):
    cake = get_object_or_404(Cake, pk=cake_id)
    return render(request, 'bakery/cake_detail.html', {'cake': cake})

def about_us(request):
    return render(request, 'bakery/about_us.html')

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

class CustomLoginView(LoginView):
    template_name = 'bakery/login.html'
    
    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().profile.full_name}! Ready to order? 🍰")
        return super().form_valid(form)

def custom_logout(request):
    logout(request)
    messages.info(request, "You have been logged out. See you soon! 👋")
    return redirect('home')

from django.shortcuts import render

# =====================================================
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
            cake=None,                    # No specific cake linked
            is_custom=True,               # Mark it as a custom order
            custom_size=custom_size,
            custom_flavour=custom_flavour,
            custom_filling=custom_filling,
            custom_frosting=custom_frosting,
            custom_decorations=custom_decorations,
            customer_notes=customer_notes,
            total_price=0,                # Price will be set by the baker
            payment_method='discuss',     # Custom orders discuss payment
            delivery_address=delivery_address,
            phone_number=phone_number,
            status='pending',
        )
        
        # Show success message
        messages.success(
            request,
            f"🎉 Your custom cake request #{order.id} has been submitted! "
            f"We will contact you shortly to confirm the details and price."
        )
        
        # Redirect back to the customise page
        return redirect('customise')
    
    # ---------- SHOW THE PAGE ----------
    return render(request, 'bakery/customise.html')