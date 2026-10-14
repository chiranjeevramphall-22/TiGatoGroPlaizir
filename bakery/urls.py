from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('our-cakes/', views.our_cakes, name='our_cakes'),
    path('cake/<int:cake_id>/', views.cake_detail, name='cake_detail'),
    path('about-us/', views.about_us, name='about_us'), 
]