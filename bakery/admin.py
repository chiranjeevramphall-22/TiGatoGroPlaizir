from django.contrib import admin
from .models import Cake, Profile, Order

# ---------- CAKE ADMIN ----------
@admin.register(Cake)
class CakeAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'image')
    search_fields = ('name',)

# ---------- PROFILE ADMIN ----------
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'phone_number')
    search_fields = ('user__username', 'full_name')

# ---------- ORDER ADMIN ----------
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'cake', 'size', 'total_price', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('customer__username', 'cake__name')
    list_editable = ('status',)   # <-- Allows you to change status directly from the list!
    
    # Groups the fields neatly in the detail view
    fieldsets = (
        ('Order Info', {
            'fields': ('customer', 'cake', 'size', 'total_price', 'status')
        }),
        ('Payment', {
            'fields': ('payment_method',)
        }),
        ('Delivery', {
            'fields': ('delivery_address', 'phone_number')
        }),
    )