from django.db import models

class Cake(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.CharField(max_length=200, help_text="Filename only, e.g., victoria-sponge.jpg")
    
    def __str__(self):
        return self.name