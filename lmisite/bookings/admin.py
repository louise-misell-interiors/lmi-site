from django.contrib import admin
from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
from solo.admin import SingletonModelAdmin
from .forms import *


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


class BookingQuestionAnswerInline(admin.StackedInline):
    model = BookingQuestionAnswer
    fields = (
        ('question',),
        ('answer',),
    )
    readonly_fields = ('question',)
    extra = 0
    max_num = 0


@admin.register(BookingType)
class BookingTypeAdmin(SortableAdminMixin, admin.ModelAdmin):
    inlines = [BookingRuleInline, BookingQuestionInline]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    inlines = [BookingQuestionAnswerInline]


class BookingInline(admin.StackedInline):
    model = Booking
    extra = 0


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    inlines = [BookingInline]


@admin.register(Config)
class ConfigAdmin(SingletonModelAdmin):
    form = ConfigForm
