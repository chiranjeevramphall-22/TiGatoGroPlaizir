from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('our-cakes/', views.our_cakes, name='our_cakes'),
    path('cake/<int:cake_id>/', views.cake_detail, name='cake_detail'),
    path('about-us/', views.about_us, name='about_us'),
    path('customise/', views.customise, name='customise'),
    
    # Authentication
    path('login/', views.CustomLoginView.as_view(), name='login'),  # <-- Changed
    path('logout/', views.custom_logout, name='logout'),
    path('signup/', views.signup, name='signup'),

    # Admin panel
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-customers/', views.admin_customers, name='admin_customers'),
    path('admin-catalogue/', views.admin_catalogue, name='admin_catalogue'),
    path('admin-catalogue/<int:cake_id>/edit/', views.admin_cake_edit, name='admin_cake_edit'),
    path('admin-catalogue/<int:cake_id>/delete/', views.admin_cake_delete, name='admin_cake_delete'),
    path('admin-customisation-options/', views.admin_customisation_options, name='admin_customisation_options'),
    path('admin-customisation-options/<int:option_id>/delete/', views.admin_customisation_option_delete, name='admin_customisation_option_delete'),
    path('admin-custom-requests/', views.admin_custom_requests, name='admin_custom_requests'),
    path('admin-orders/', views.admin_orders, name='admin_orders'),
]