import datetime

import dateutil.parser
import googleapiclient.discovery
import graphene.types.datetime
import main_site.views
import pytz
import requests
import stripe
import decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from graphene_django import DjangoObjectType
from main_site.models import SiteConfig

from . import models
from .views import API_SERVICE_NAME, API_VERSION, get_credentials, booking_succeeded


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


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

        calendars = calendar.calendarList().list().execute()
        calendars = filter(lambda c: c.get("primary", False), calendars.get('items', []))

        for c in calendars:
            events = calendar.events() \
                .list(calendarId=c['id'], orderBy='startTime', singleEvents=True,
                      timeMin=datetime.datetime.combine(start_date, datetime.time.min).isoformat() + 'Z',
                      timeMax=datetime.datetime.combine(end_date, datetime.time.max).isoformat() + 'Z') \
                .execute()

            events = filter(lambda e: e.get("status", "") == 'confirmed' and e.get('kind', '') == 'calendar#event',
                            events.get('items', []))
            for event in events:
                start = event['start'].get('dateTime')
                end = event['end'].get('dateTime')
                if start and end:
                    start = timezone.make_naive(dateutil.parser.parse(start)).date()
                    end = timezone.make_naive(dateutil.parser.parse(end)).date()
                    cur_date = start
                    while cur_date <= end:
                        if out.get(cur_date) is not None:
                            out[cur_date].append(event)
                        cur_date += datetime.timedelta(hours=24)

    return out


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

        cur_date = cur_time.date()
        week_start = cur_date - datetime.timedelta(days=cur_date.weekday())
        week_end = week_start + datetime.timedelta(days=6)
        bookings_on_day = models.Booking.objects.filter(time__date=cur_date, pending=False)
        bookings_this_type_on_day = models.Booking.objects.filter(time__date=cur_date, pending=False, type=booking)
        bookings_in_week = models.Booking.objects.filter(time__gt=week_start, time__lt=week_end, pending=False)
        bookings_this_type_in_week = models.Booking.objects.filter(
            time__gt=week_start, time__lt=week_end, pending=False, type=booking)
        bookings_in_month = models.Booking.objects.filter(time__month=cur_date.month, pending=False)
        bookings_this_type_in_month = models.Booking.objects.filter(
            time__month=cur_date.month, pending=False, type=booking)
        while cur_time.time() <= datetime.time(23) and cur_date == date:
            valid = True

            if cur_time < now:
                valid = False
            if (now + booking.minimum_scheduling_notice) > cur_time:
                valid = False

            passes_rules = False
            if valid:
                for rule in rules:
                    if rule.start_date > cur_date:
                        continue
                    if not rule.recurring and rule.end_date < cur_date:
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
                        datetime.datetime.combine(date, rule.start_time), tz)
                                                     .astimezone(pytz.utc))
                    end_time = timezone.make_naive(timezone.make_aware(
                        datetime.datetime.combine(date, rule.end_time), tz)
                                                   .astimezone(pytz.utc))
                    if not (start_time <= cur_time and end_time >= (cur_time + booking.length)):
                        continue

                    passes_rules = True
            if not passes_rules:
                valid = False

            if valid:
                if booking.max_events_per_day is not None and len(bookings_on_day) >= booking.max_events_per_day:
                    valid = False
                elif booking.max_events_per_day_this_event is not None \
                        and len(bookings_this_type_on_day) >= booking.max_events_per_day_this_event:
                    valid = False
                elif booking.max_events_per_week is not None and len(bookings_in_week) >= booking.max_events_per_week:
                    valid = False
                elif booking.max_events_per_week_this_event is not None \
                        and len(bookings_this_type_in_week) >= booking.max_events_per_week_this_event:
                    valid = False
                elif booking.max_events_per_month is not None and \
                        len(bookings_in_month) >= booking.max_events_per_month:
                    valid = False
                elif booking.max_events_per_month_this_event is not None and \
                        len(bookings_this_type_in_month) >= booking.max_events_per_month_this_event:
                    valid = False
                else:
                    for b in bookings_on_day:
                        time = timezone.make_naive(b.time)
                        if cur_time >= time - max(booking.buffer_after_event, b.type.buffer_before_event) and \
                                cur_time + booking.length <= time + b.type.length + \
                                max(booking.buffer_before_event, b.type.buffer_after_event):
                            valid = False

            if valid:
                for b in cal_events[date]:
                    start = b['start'].get('dateTime')
                    end = b['end'].get('dateTime')
                    if start and end:
                        start = timezone.make_naive(dateutil.parser.parse(start))
                        end = timezone.make_naive(dateutil.parser.parse(end))
                        if cur_time >= start - booking.buffer_before_event and \
                                cur_time + booking.length <= end + booking.buffer_after_event:
                            valid = False

            if valid:
                times.append(cur_time.time())

            cur_time += booking.scheduling_frequency
            cur_date = cur_time.date()

        out[date] = times
        date += datetime.timedelta(days=1)

    return out


class BookingQuestion(DjangoObjectType):
    class Meta:
        model = models.BookingQuestion


class BookingType(DjangoObjectType):
    class Meta:
        model = models.BookingType
        only_fields = (
            'name', 'length', 'id', 'description', 'whilst_booking_message', 'after_booking_message', 'timezone',
            'icon', 'price')

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
            return get_booking_times(start, self, start + datetime.timedelta(days=(num-1)))

        while len(days) < num:
            new_days = get_days(day)
            for d, t in new_days.items():
                if len(days) >= num:
                    break
                if len(t) > 0:
                    num_tried = 0
                    days.append(d)
            num_tried += len(new_days)
            day = day + datetime.timedelta(days=num)
            if len(days) == 0 and num_tried >= 365:
                break
            elif len(days) != 0 and num_tried >= 30:
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
    return map(lambda item: QuestionError(field=item[0], errors=item[1]), error)


class CreateBooking(graphene.Mutation):
    class Arguments:
        id = graphene.ID(required=True)
        date = graphene.Date(required=True)
        time = graphene.Time(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        phone = graphene.String(required=True)
        newsletter = graphene.Boolean(required=True)
        files = graphene.List(graphene.NonNull(graphene.String), required=True)
        questions = graphene.List(
            QuestionInput,
            required=True
        )

    ok = graphene.Boolean()
    payment_intent_id = graphene.String()
    error = graphene.List(QuestionError)

    def mutate(self, info, id, date, time, first_name, last_name, email, phone, newsletter, files, questions):
        config = SiteConfig.objects.first()
        booking_type = models.BookingType.objects.get(pk=id)

        booking = models.Booking(pending=False)

        matching_customers = models.Customer.objects.filter(email=email)
        if len(matching_customers) > 0:
            customer = matching_customers.first()
        else:
            customer = models.Customer()
            customer.email = email

            creds = main_site.views.get_newsletter_credentials()
            if creds is not None and config.newsletter_group_id:
                member = requests.post(f"{creds['endpoint']}/3.0/lists/{config.newsletter_group_id}/members/", headers={
                    "Authorization": f"OAuth {creds['token']}"
                }, json={
                    "email_address": email,
                    "status": "subscribed" if newsletter else "unsubscribed",
                    "source": "Website",
                    "ip_signup": get_client_ip(info.context),
                    "merge_fields": {
                        "FNAME": first_name,
                        "LNAME": last_name
                    }
                })
                if member.status_code == 200:
                    data = member.json()
                    customer.mailchimp_id = data.get("id", "")

        customer.first_name = first_name
        customer.last_name = last_name
        customer.phone = phone

        try:
            customer.full_clean()
        except ValidationError as e:
            return CreateBooking(ok=False, error=validation_error_to_graphene(e))

        booking_times = get_booking_times(date, booking_type)[date]

        if time not in booking_times:
            return CreateBooking(ok=False, error=validation_error_to_graphene([('time', ["Unavailable booking time"])]))

        customer.save()

        time = timezone.make_aware(datetime.datetime.combine(date, time), pytz.utc)
        booking.time = time
        booking.type = booking_type
        booking.customer = customer

        try:
            booking.full_clean()
        except ValidationError as e:
            return CreateBooking(ok=False, error=validation_error_to_graphene(e))

        seen_questions = []
        booking_question_answers = []
        for question in questions:
            try:
                booking_question = models.BookingQuestion.objects.get(id=question.id)
            except models.BookingQuestion.DoesNotExist:
                return CreateBooking(
                    ok=False,
                    error=validation_error_to_graphene([('question', ['Question doesn\'t exist'])])
                )

            if booking_question.required and len(question.value.strip()) == 0:
                return CreateBooking(
                    ok=False,
                    error=validation_error_to_graphene([(question.id, [f'"{booking_question.question}" is required'])])
                )
            seen_questions.append(str(question.id))

            booking_question_answer = models.BookingQuestionAnswer()
            booking_question_answer.answer = question.value
            booking_question_answer.question = booking_question
            booking_question_answers.append(booking_question_answer)

        for question in booking_type.booking_questions.all():
            if str(question.id) not in seen_questions and question.required:
                return CreateBooking(
                    ok=False,
                    error=validation_error_to_graphene([(question.id, [f'"{question.question}" is required'])])
                )

        booking.save()
        for booking_question_answer in booking_question_answers:
            booking.booking_question_answers.add(booking_question_answer, bulk=False)

        for file in files:
            booking_file = models.BookingFile(
                booking=booking,
                file=file
            )
            booking_file.save()

        if booking_type.price:
            pi = stripe.PaymentIntent.create(
                amount=int(booking_type.price * decimal.Decimal('100')),
                currency='gbp',
                description=booking_type.name,
                setup_future_usage='off_session',
                payment_method_options={
                    "card": {
                        "request_three_d_secure": "any"
                    }
                }
            )
            booking.stripe_payment_intent_id = pi.id
            booking.pending = True
            booking.save()

            return CreateBooking(ok=True, payment_intent_id=pi.client_secret)
        else:
            booking_succeeded(booking)
            return CreateBooking(ok=True)


class ConfigType(DjangoObjectType):
    class Meta:
        model = models.Config
        only_fields = ('booking_notice',)


class Query(graphene.ObjectType):
    booking_config = graphene.Field(ConfigType)
    booking_types = graphene.NonNull(graphene.List(graphene.NonNull(BookingType)))
    booking_type = graphene.Field(
        BookingType,
        id=graphene.ID(required=True)
    )

    def resolve_booking_types(self, info):
        return models.BookingType.objects.filter(hidden=False)

    def resolve_booking_type(self, info, id):
        return models.BookingType.objects.get(pk=id)

    def resolve_config(self, info):
        return models.Config.objects.first()


class Mutation(graphene.ObjectType):
    create_booking = CreateBooking.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
