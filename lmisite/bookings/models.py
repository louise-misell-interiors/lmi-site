from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class BookingType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    length = models.TimeField()

    def __str__(self):
        return self.name


class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = PhoneNumberField()
    email = models.EmailField()


class Booking(models.Model):
    type = models.ForeignKey(BookingType, related_name='bookings', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, related_name='bookings', on_delete=models.CASCADE)
    time = models.DateTimeField()
    address = models.TextField()