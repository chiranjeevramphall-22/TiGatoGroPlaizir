from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('our-cakes/', views.our_cakes, name='our_cakes'),
    path('cake/<int:cake_id>/', views.cake_detail, name='cake_detail'),
    path('about-us/', views.about_us, name='about_us'),
    
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='bakery/login.html'), name='login'),
    path('signup/', auth_views.LoginView.as_view(template_name='bakery/signup.html'), name='signup'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]