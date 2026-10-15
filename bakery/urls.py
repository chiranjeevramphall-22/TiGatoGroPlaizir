from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('our-cakes/', views.our_cakes, name='our_cakes'),
    path('cake/<int:cake_id>/', views.cake_detail, name='cake_detail'),
    path('about-us/', views.about_us, name='about_us'),
    
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),  # <-- Changed
    path('logout/', views.custom_logout, name='logout'),
    path('signup/', views.signup, name='signup'),
]