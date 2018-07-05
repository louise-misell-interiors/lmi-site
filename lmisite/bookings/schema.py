from graphene_django import DjangoObjectType
import datetime
import graphene.types.datetime
from django.utils import timezone
import pytz
import googleapiclient.discovery
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from main_site.models import SiteConfig
from . import models
import dateutil.parser
from .views import API_SERVICE_NAME, API_VERSION, get_credentials


def get_calendar_events(date: datetime.date):
    creds = get_credentials()
    calendar = googleapiclient.discovery.build(
        API_SERVICE_NAME, API_VERSION, credentials=creds)

    events = calendar.events()\
        .list(calendarId="primary", orderBy='startTime', singleEvents=True,
              timeMin=datetime.datetime.combine(date, datetime.time.min).isoformat() + 'Z',
              timeMax=datetime.datetime.combine(date, datetime.time.max).isoformat() + 'Z')\
        .execute()

    return list(filter(lambda event: event.get("status", "") == 'confirmed' and event.get('kind', '') == 'calendar#event', events.get('items', [])))


def get_booking_times(date: datetime.date, booking: models.BookingType):
    tz = pytz.timezone(booking.timezone)

    times = []
    cur_time = datetime.datetime.combine(date, datetime.datetime.min.time())

    now = datetime.datetime.now()
    rules = booking.booking_rules.all()
    bookings_on_day = models.Booking.objects.filter(time__date=cur_time.date())
    cal_events = get_calendar_events(date)
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

                start_time = timezone.make_aware(
                    datetime.datetime.combine(datetime.datetime(1970, 1, 1), rule.start_time), tz)\
                    .astimezone(pytz.utc).time()
                end_time = timezone.make_aware(
                    datetime.datetime.combine(datetime.datetime(1970, 1, 1), rule.end_time), tz)\
                    .astimezone(pytz.utc).time()
                if not (start_time <= cur_time.time() and end_time >= (cur_time + booking.length).time()):
                    continue

                passes_rules = True
        if not passes_rules:
            valid = False

        if valid:
            if booking.max_events_per_day is not None and len(bookings_on_day) >= booking.max_events_per_day:
                valid = False
            else:
                for b in bookings_on_day:
                    time = timezone.make_naive(b.time)
                    if time <= cur_time < (
                            time + b.type.length + max(booking.buffer_before_event, b.type.buffer_after_event)):
                        valid = False
                    if time < (
                            cur_time + booking.length + max(booking.buffer_after_event, b.type.buffer_before_event)) < (
                            time + b.type.length):
                        valid = False
            for b in cal_events:
                start = b['start'].get('dateTime')
                end = b['end'].get('dateTime')
                if start and end:
                    start = timezone.make_naive(dateutil.parser.parse(start))
                    end = timezone.make_naive(dateutil.parser.parse(end))
                    if start <= cur_time < (end + booking.buffer_before_event):
                        valid = False
                    if start < (cur_time + booking.length + booking.buffer_after_event) < end:
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

        subject = f"{name} has booked {booking_type.name}"
        time = datetime.datetime.combine(date, time).strftime("%I:%M%p %a %d %b %Y")
        body = f"Name: {name}\r\nEmail: {email}\r\nPhone: {phone}\r\n\r\n---\r\n\r\n{booking_type.name}\r\nTime: {time}"

        config = SiteConfig.objects.first()
        recipients = [config.email]
        send_mail(subject, body, email, recipients)

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
