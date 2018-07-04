from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from .models import *


class BookingRuleInline(SortableInlineAdminMixin, admin.StackedInline):
    model = BookingRule
    fields = (
        ('start_time', 'end_time'),
        ('recurring', 'start_date', 'end_date'),
        ('monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'),
    )
    extra = 1


class BookingQuestionInline(SortableInlineAdminMixin, admin.StackedInline):
    model = BookingQuestion
    fields = (
        ('question',),
        ('question_type', 'required'),
    )
    extra = 1


@admin.register(BookingType)
class BookingTypeAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [BookingRuleInline, BookingQuestionInline]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    pass


class BookingInline(admin.StackedInline):
    model = Booking
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    inlines = [BookingInline]
