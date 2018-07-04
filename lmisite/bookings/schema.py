from graphene_django import DjangoObjectType
import datetime
import graphene.types.datetime
from django.utils import timezone
import pytz
from django.core.exceptions import ValidationError
from . import models


def get_booking_times(date: datetime.date, booking: models.BookingType):
    tz = pytz.timezone(booking.timezone)

    times = []
    cur_time = timezone.make_aware(datetime.datetime.combine(date, datetime.datetime.min.time())
                                   .replace(hour=0, minute=0, second=0, microsecond=0), tz)

    now = timezone.now()
    rules = booking.booking_rules.all()
    while cur_time.time() <= datetime.time(23):
        valid = True

        if cur_time < now:
            valid = False
        if (now + booking.minimum_scheduling_notice) > cur_time:
            valid = False

        passes_rules = False
        if valid:
            for rule in rules:
                if rule.start_date > cur_time.date():
                    continue
                if not rule.recurring and rule.end_date < cur_time.date():
                    continue

                if not rule.monday and cur_time.weekday() == 0:
                    continue
                if not rule.tuesday and cur_time.weekday() == 1:
                    continue
                if not rule.wednesday and cur_time.weekday() == 2:
                    continue
                if not rule.thursday and cur_time.weekday() == 3:
                    continue
                if not rule.friday and cur_time.weekday() == 4:
                    continue
                if not rule.saturday and cur_time.weekday() == 5:
                    continue
                if not rule.sunday and cur_time.weekday() == 6:
                    continue

                if not (rule.start_time <= cur_time.time() and rule.end_time >= (cur_time + booking.length).time()):
                    continue

                passes_rules = True
            if not passes_rules:
                valid = False

        if valid:
            for b in models.Booking.objects.filter(time__date=cur_time.date()):
                if b.time <= cur_time < (b.time + b.type.length + booking.buffer_before_event):
                    valid = False
                if b.time < (cur_time + booking.length + booking.buffer_after_event) < (b.time + b.type.length):
                    valid = False

        if valid:
            times.append(cur_time.time())
        cur_time += booking.scheduling_frequency

    return times


class BookingQuestion(DjangoObjectType):
    class Meta:
        model = models.BookingQuestion


class BookingType(DjangoObjectType):
    class Meta:
        model = models.BookingType
        only_fields = ('name', 'length', 'id', 'description', 'timezone')

    scheduling_frequency = graphene.String()
    minimum_scheduling_notice = graphene.String()
    length = graphene.String()

    booking_days = graphene.List(
        graphene.types.datetime.Date,
        num=graphene.Int(default_value=5),
        start=graphene.Date(default_value=datetime.datetime.now().date())
    )

    booking_times = graphene.List(
        graphene.types.datetime.Time,
        date=graphene.Date(required=True)
    )

    questions = graphene.List(
        BookingQuestion
    )

    def resolve_questions(self, info):
        return self.booking_questions.all()

    def resolve_booking_times(self, info, date):
        return get_booking_times(date, self)

    def resolve_booking_days(self, info, start, num):
        days = []
        day = start
        num_tried = 0
        while len(days) < num:
            if len(get_booking_times(day, self)) > 0:
                days.append(day)
            else:
                num_tried += 1
                if num_tried >= 60:
                    break
            day += datetime.timedelta(days=1)

        return days


class QuestionInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    value = graphene.String(required=True)


class CreateBooking(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        date = graphene.Date(required=True)
        time = graphene.Time(required=True)
        name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=True)
        questions = graphene.List(
            QuestionInput,
            required=True
        )

    ok = graphene.Boolean()
    error = graphene.List(
        graphene.String
    )

    def mutate(self, info, id, date, time, name, email, phone, questions):
        booking_type = models.BookingType.objects.get(pk=id)
        tz = pytz.timezone(booking_type.timezone)
        booking_times = get_booking_times(date, booking_type)

        if time not in booking_times:
            return CreateBooking(ok=False, error=["Unavailable booking time"])

        booking = models.Booking()

        matching_customers = models.Customer.objects.filter(email=email)
        if len(matching_customers) > 0:
            customer = matching_customers.first()
        else:
            customer = models.Customer()
            customer.email = email
        customer.name = name
        customer.phone = phone

        try:
            customer.full_clean()
        except ValidationError as e:
            return CreateBooking(ok=False, error=map(lambda error: error[0].title() + ": " + error[1][0], e))
        customer.save()

        booking.time = timezone.make_aware(datetime.datetime.combine(date, time), tz)
        booking.type = booking_type
        booking.customer = customer

        try:
            booking.full_clean()
        except ValidationError as e:
            return CreateBooking(ok=False, error=map(lambda error: error[0].title() + ": " + error[1][0], e))
        booking.save()

        return CreateBooking(ok=True, error="")


class Query(graphene.ObjectType):
    booking_types = graphene.List(BookingType)
    booking_type = graphene.Field(
        BookingType,
        id=graphene.ID(required=True)
    )

    def resolve_booking_types(self, info):
        return models.BookingType.objects.all()

    def resolve_booking_type(self, info, id):
        return models.BookingType.objects.get(pk=id)


class Mutation(graphene.ObjectType):
    create_booking = CreateBooking.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
