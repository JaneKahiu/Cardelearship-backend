from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.user.username

# inquiry model
class Inquiry(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='inquiries')
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
         return f"Inquiry by {self.customer.user.username}: {self.subject}"
#car model
class Car(models.Model):
    make = models.CharField(max_length=255)
    image = models.ImageField(upload_to='cars/', default='default_image.png')
    model = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.year} {self.make} {self.model}"
    def get_price_in_usd(self, conversion_rate=0.0068):
        return round(self.price * conversion_rate, 2)