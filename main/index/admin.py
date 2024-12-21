from django.contrib import admin

# Register your models here.
from .models import Customer, Inquiry, Car
admin.site.register(Customer)
admin.site.register(Inquiry)
admin.site.register(Car)
