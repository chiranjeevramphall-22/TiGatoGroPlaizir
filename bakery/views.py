from django.shortcuts import render, get_object_or_404
from .models import Cake

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