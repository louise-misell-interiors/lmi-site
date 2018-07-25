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


def get_calendar_events(start_date: datetime.date, end_date: datetime.date):
    creds = get_credentials()
    out = {}
    date = start_date
    while date <= end_date:
        out[date] = []
        date += datetime.timedelta(days=1)
    if creds is not None:
        calendar = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=creds)

        events = calendar.events()\
            .list(calendarId="primary", orderBy='startTime', singleEvents=True,
                  timeMin=datetime.datetime.combine(start_date, datetime.time.min).isoformat() + 'Z',
                  timeMax=datetime.datetime.combine(end_date, datetime.time.max).isoformat() + 'Z')\
            .execute()

        events = filter(lambda e: e.get("status", "") == 'confirmed' and e.get('kind', '') == 'calendar#event', events.get('items', []))
        for event in events:
            start = event['start'].get('dateTime')
            if start:
                start = timezone.make_naive(dateutil.parser.parse(start)).date()
                out[start].append(event)

    return out


def insert_booking_to_calendar(booking: models.Booking):
    creds = get_credentials()
    if creds is not None:
        calendar = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=creds)

        calendar.events().insert(calendarId="primary", body={
            "start": {
                "dateTime": booking.time.isoformat(),
                "timeZone": booking.time.tzname()
            },
            "end": {
                "dateTime": (booking.time + booking.type.length).isoformat(),
                "timeZone": (booking.time + booking.type.length).tzname()
            },
            "summary": str(booking),
            "attendees": [
                {
                    "displayName": booking.customer.name,
                    "responseStatus": "accepted",
                    "email": booking.customer.email,
                    "comment": f"Phone: {booking.customer.phone}"
                }
            ],
        }, sendNotifications=True).execute()


def get_booking_times(start_date: datetime.date, booking: models.BookingType, end_date=None):
    if end_date is None:
        end_date = start_date

    tz = pytz.timezone(booking.timezone)
    cal_events = get_calendar_events(start_date, end_date)
    rules = booking.booking_rules.all()
    now = datetime.datetime.now()

    out = {}

    date = start_date
    while date <= end_date:
        times = []
        cur_time = datetime.datetime.combine(date, datetime.datetime.min.time())

        bookings_on_day = models.Booking.objects.filter(time__date=cur_time.date())
        while cur_time.time() <= datetime.time(23) and cur_time.date() == date:
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

                    start_time = timezone.make_naive(timezone.make_aware(
                        datetime.datetime.combine(date, rule.start_time), tz)\
                        .astimezone(pytz.utc))
                    end_time = timezone.make_naive(timezone.make_aware(
                        datetime.datetime.combine(date, rule.end_time), tz)\
                        .astimezone(pytz.utc))
                    if not (start_time <= cur_time and end_time >= (cur_time + booking.length)):
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

            if valid:
                for b in cal_events[date]:
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

        out[date] = times
        date += datetime.timedelta(days=1)

    return out


class BookingQuestion(DjangoObjectType):
    class Meta:
        model = models.BookingQuestion


class BookingType(DjangoObjectType):
    class Meta:
        model = models.BookingType
        only_fields = ('name', 'length', 'id', 'description', 'whilst_booking_message', 'after_booking_message', 'timezone', 'icon')

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
        return get_booking_times(date, self)[date]

    def resolve_booking_days(self, info, start, num):
        days = []
        day = start
        num_tried = 0

        def get_days(start):
            return get_booking_times(start, self, start + datetime.timedelta(days=num))

        while len(days) < num:
            new_days = get_days(day)
            for d, t in new_days.items():
                if len(t) > 0 and len(days) < num:
                    days.append(d)
            num_tried += len(new_days)
            if len(days) > 0:
                day = days[-1] + datetime.timedelta(days=1)
            else:
                day = day + datetime.timedelta(days=len(new_days))
            if num_tried >= 60:
                break

        return days


class QuestionInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
    value = graphene.String(required=True)


class QuestionError(graphene.ObjectType):
    field = graphene.String(required=True)
    errors = graphene.List(
        graphene.String,
        required=True
    )


def validation_error_to_graphene(error):
    def map_func(item):
        return QuestionError(
            field=item[0],
            errors=item[1]
        )
    return map(map_func, error)


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
    error = graphene.List(QuestionError)

    def mutate(self, info, id, date, time, name, email, phone, questions):
        booking_type = models.BookingType.objects.get(pk=id)
        booking_times = get_booking_times(date, booking_type)[date]

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
            return CreateBooking(ok=False, error=validation_error_to_graphene(e))
        customer.save()

        time = timezone.make_aware(datetime.datetime.combine(date, time), pytz.utc)
        booking.time = time
        booking.type = booking_type
        booking.customer = customer

        try:
            booking.full_clean()
        except ValidationError as e:
            return CreateBooking(ok=False, error=validation_error_to_graphene(e))
        # booking.save()

        subject = f"{name} has booked {booking_type.name}"
        tz = pytz.timezone(booking_type.timezone)
        time = time.astimezone(tz=tz).strftime("%I:%M%p %a %d %b %Y")
        body = f"Name: {name}\r\nEmail: {email}\r\nPhone: {phone}\r\n\r\n---\r\n\r\n{booking_type.name}\r\n" \
               f"Time: {time}, {booking_type.timezone}"

        config = SiteConfig.objects.first()
        recipients = [config.email]
        send_mail(subject, body, email, recipients)

        insert_booking_to_calendar(booking)

        return CreateBooking(ok=True, error=[])


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
