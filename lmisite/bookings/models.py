from django.db import models
import datetime
import pytz
from django.core.validators import ValidationError
from phonenumber_field.modelfields import PhoneNumberField
from solo.models import SingletonModel


class BookingType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    whilst_booking_message = models.TextField(blank=True)
    after_booking_message = models.TextField(blank=True)
    length = models.DurationField()
    order = models.PositiveIntegerField(default=0, blank=True, null=False)
    icon = models.CharField(max_length=255, blank=True)

    max_events_per_day = models.PositiveIntegerField(blank=True, null=True)
    minimum_scheduling_notice = models.DurationField(default=datetime.timedelta())
    scheduling_frequency = models.DurationField(default=datetime.timedelta(0, 30))
    buffer_before_event = models.DurationField(default=datetime.timedelta())
    buffer_after_event = models.DurationField(default=datetime.timedelta())

    timezone = models.CharField(max_length=255, default="Europe/London")

    class Meta:
        ordering = ['order']

    def clean(self):
        try:
            pytz.timezone(self.timezone)
        except pytz.UnknownTimeZoneError:
            raise ValidationError("Invalid timezone")

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class BookingRule(models.Model):
    type = models.ForeignKey(BookingType, related_name='booking_rules', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    start_time = models.TimeField(default=datetime.time())
    end_time = models.TimeField(default=datetime.time())

    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    monday = models.BooleanField()
    tuesday = models.BooleanField()
    wednesday = models.BooleanField()
    thursday = models.BooleanField()
    friday = models.BooleanField()
    saturday = models.BooleanField()
    sunday = models.BooleanField()

    def __str__(self):
        return "#" + str(self.pk)

    @property
    def recurring(self):
        return self.end_date is None

    class Meta:
        ordering = ['order']


class BookingQuestion(models.Model):
    type = models.ForeignKey(BookingType, related_name='booking_questions', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, blank=True, null=False)

    question = models.CharField(max_length=255)
    required = models.BooleanField()

    TYPES = (
        ("T", "One Line"),
        ("M", "Multi-line"),
    )

    question_type = models.CharField(max_length=1, choices=TYPES)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ['order']


class Customer(models.Model):
    name = models.CharField(max_length=255)
    phone = PhoneNumberField()
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    type = models.ForeignKey(BookingType, related_name='bookings', on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, related_name='bookings', on_delete=models.CASCADE)
    time = models.DateTimeField()

    def __str__(self):
        return f"{self.type.name} with {self.customer.name}"


class BookingQuestionAnswer(models.Model):
    booking = models.ForeignKey(Booking, related_name='booking_question_answers', on_delete=models.CASCADE)
    question = models.ForeignKey(BookingQuestion, related_name='answers', on_delete=models.CASCADE)

    answer = models.TextField()

    def __str__(self):
        return f"{self.booking}: {self.question}"


class Config(SingletonModel):
    google_credentials = models.TextField()

    def __str__(self):
        return "Config"
