from django.contrib import admin
from .models import *


@admin.register(BookingType)
class BookingTypeAdmin(admin.ModelAdmin):
    pass