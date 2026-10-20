from django.contrib import admin
from .models import Cake, Profile, Order, CustomisationOption

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
    list_display = ('id', 'customer', 'get_order_type', 'get_cake_name', 'total_price', 'payment_method', 'status', 'created_at')
    list_filter = ('status', 'payment_method', 'is_custom', 'created_at')
    search_fields = ('customer__username', 'cake__name')
    list_editable = ('status',)
    
    fieldsets = (
        ('Order Info', {
            'fields': ('customer', 'is_custom', 'cake', 'total_price', 'status')
        }),
        ('Standard Cake', {
            'fields': ('size',),
            'classes': ('collapse',)
        }),
        ('Custom Cake Details', {
            'fields': ('custom_size', 'custom_flavour', 'custom_filling', 'custom_frosting', 'custom_decorations', 'customer_notes'),
            'classes': ('collapse',)
        }),
        ('Payment', {
            'fields': ('payment_method',)
        }),
        ('Delivery', {
            'fields': ('delivery_address', 'phone_number')
        }),
    )
    
    # A helper column: shows "CUSTOM" or "STANDARD"
    def get_order_type(self, obj):
        return "CUSTOM" if obj.is_custom else "Standard"
    get_order_type.short_description = "Type"
    
    # A helper column: shows the cake name, or the custom flavour
    def get_cake_name(self, obj):
        if obj.is_custom:
            return f"{obj.custom_size} - {obj.custom_flavour}"
        return obj.cake.name if obj.cake else "Deleted"
    get_cake_name.short_description = "Cake"


# ---------- CUSTOMISATION OPTION ADMIN ----------
# Provides a backup management interface in Django's built-in admin.
@admin.register(CustomisationOption)
class CustomisationOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('name',)