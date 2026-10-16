from django.shortcuts import render, get_object_or_404
from .models import Cake
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

def customise(request):
    return render(request, 'bakery/customise.html')