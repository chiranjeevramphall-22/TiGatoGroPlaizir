from django.db import models
from django.contrib.auth.models import User

class Cake(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=200, help_text="Filename only, e.g., victoria-sponge.jpg")
    
    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    phone_number = models.CharField(max_length=20, blank=True)
    delivery_address = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.full_name}"    

# =====================================================
# ORDER MODEL
# Stores every cake order placed by a customer.
# =====================================================
class Order(models.Model):
    
    # ---------- STATUS CHOICES ----------
    STATUS_CHOICES = [
        ('pending', 'Pending'),           # Just placed, awaiting confirmation
        ('confirmed', 'Confirmed'),       # Admin confirmed
        ('baking', 'Baking'),             # Being made
        ('ready', 'Ready for Pickup'),    # Ready
        ('delivered', 'Delivered'),       # Completed
        ('cancelled', 'Cancelled'),       # Cancelled
    ]
    
    # ---------- PAYMENT CHOICES ----------
    PAYMENT_CHOICES = [
        ('mcb_juice', 'MCB Juice'),
        ('cod', 'Cash on Delivery'),
    ]
    
    # ---------- RELATIONSHIPS ----------
    customer = models.ForeignKey(User, on_delete=models.CASCADE)   # Who ordered
    cake = models.ForeignKey(Cake, on_delete=models.SET_NULL, null=True)  # Which cake
    
    # ---------- ORDER DETAILS ----------
    size = models.CharField(max_length=50, default='Small (6")')   # Size chosen
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    
    # ---------- CUSTOMER INFO ----------
    delivery_address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # ---------- STATUS & TIMESTAMPS ----------
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)   # Auto-set when created
    updated_at = models.DateTimeField(auto_now=True)       # Auto-updated on change
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.username} - {self.cake.name if self.cake else 'Deleted'}"