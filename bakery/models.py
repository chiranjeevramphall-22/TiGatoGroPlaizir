from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static

class Cake(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=200, blank=True, help_text="Filename only, e.g., victoria-sponge.jpg")
    photo = models.ImageField(upload_to='cakes/', blank=True)
    is_available = models.BooleanField(default=True)

    @property
    def image_url(self):
        if self.photo:
            return self.photo.url
        if self.image:
            return static('images/' + self.image)
        return ''
 
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
# Can be a standard cake OR a custom-built cake.
# =====================================================
class Order(models.Model):
    
    # ---------- STATUS CHOICES ----------
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('baking', 'Baking'),
        ('ready', 'Ready for Pickup'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    # ---------- PAYMENT CHOICES ----------
    PAYMENT_CHOICES = [
        ('mcb_juice', 'MCB Juice'),
        ('cod', 'Cash on Delivery'),
        ('discuss', 'To Be Discussed with Baker'),   # Used for custom orders
    ]
    
    # ---------- RELATIONSHIPS ----------
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    cake = models.ForeignKey(Cake, on_delete=models.SET_NULL, null=True, blank=True)  # Can be NULL for custom orders
    
    # ---------- ORDER TYPE ----------
    is_custom = models.BooleanField(default=False)   # True if this is a custom cake order
    
    # ---------- STANDARD CAKE DETAILS ----------
    size = models.CharField(max_length=50, blank=True)
    
    # ---------- CUSTOM CAKE DETAILS (only used if is_custom = True) ----------
    custom_size = models.CharField(max_length=50, blank=True)
    custom_flavour = models.CharField(max_length=50, blank=True)
    custom_filling = models.CharField(max_length=50, blank=True)
    custom_frosting = models.CharField(max_length=50, blank=True)
    custom_decorations = models.TextField(blank=True)   # Comma-separated list
    
    # ---------- PRICING & PAYMENT ----------
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='discuss')
    
    # ---------- CUSTOMER INFO ----------
    delivery_address = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    
    # ---------- NOTES ----------
    customer_notes = models.TextField(blank=True, help_text="Any extra requests from the customer")
    
    # ---------- STATUS & TIMESTAMPS ----------
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        if self.is_custom:
            return f"Order #{self.id} - CUSTOM - {self.customer.username}"
        return f"Order #{self.id} - {self.customer.username} - {self.cake.name if self.cake else 'Deleted'}"

    # ---------- EVENT DETAILS (Optional extended form) ----------
    cake_type = models.CharField(max_length=100, blank=True)
    theme = models.CharField(max_length=100, blank=True)
    colour_scheme = models.CharField(max_length=100, blank=True)
    required_date = models.DateField(null=True, blank=True)
    personalised_message = models.TextField(blank=True)
    # ---------- ADMIN NOTES ----------
    admin_notes = models.TextField(blank=True, help_text="Internal notes from the baker")
    # ---------- PAYMENT REFERENCE ----------
    payment_reference = models.CharField(max_length=100, blank=True, help_text="Reference ID from MCB Juice or Bank Transfer")
    bank_name = models.CharField(max_length=100, blank=True, help_text="If paid by Bank Transfer")

    # ---------- FULFILMENT METHOD ----------
    FULFILMENT_CHOICES = [
        ('pickup', 'Pick Up'),
        ('delivery', 'Delivery'),
    ]
    fulfilment_method = models.CharField(
        max_length=20, 
        choices=FULFILMENT_CHOICES, 
        default='pickup',
        help_text="Did the customer choose Pick Up or Delivery?"
    )

# =====================================================
# CUSTOMISATION OPTION MODEL
# Stores every size, flavour, filling, frosting and
# decoration that an administrator makes available to
# customers on the Customise page.
# =====================================================
class CustomisationOption(models.Model):

    CATEGORY_CHOICES = [
        ('size', 'Sizes'),
        ('flavour', 'Flavours'),
        ('filling', 'Fillings'),
        ('frosting', 'Frostings'),
        ('decoration', 'Decorations'),
    ]

    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'name'],
                name='unique_customisation_option',
            )
        ]

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"