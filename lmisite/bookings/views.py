from django.shortcuts import render, redirect, reverse
from django.views.decorators.http import require_POST
from django.http import HttpResponseBadRequest, HttpResponse
from django.core.files.storage import FileSystemStorage
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from main_site.models import SiteConfig
import googleapiclient.discovery
import json
import google_auth_oauthlib.flow
import google.oauth2.credentials
from .models import *
import requests

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/calendar']
API_SERVICE_NAME = 'calendar'
API_VERSION = 'v3'


def index(request):
    return render(request, "bookings/index.html")


@require_POST
def upload_file(request):
    if not len(request.FILES):
        return HttpResponseBadRequest()

    file = next(request.FILES.values())
    fs = FileSystemStorage()
    filename = fs.save(file.name, file)
    uploaded_file_url = fs.url(filename)

    return HttpResponse(json.dumps({
        "url": uploaded_file_url
    }), content_type="application/json")


def authorise(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    uri = request.build_absolute_uri(reverse('bookings:oauth'))
    if not settings.DEBUG:
        uri = uri.replace("http://", "https://")
    flow.redirect_uri = uri

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true')

    request.session['state'] = state
    request.session['redirect'] = request.META.get('HTTP_REFERER')

    return redirect(authorization_url)


def oauth(request):
    state = request.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    uri = request.build_absolute_uri(reverse('bookings:oauth'))
    if not settings.DEBUG:
        uri = uri.replace("http://", "https://")
    flow.redirect_uri = uri

    flow.fetch_token(code=request.GET.get("code"))

    credentials = flow.credentials
    config = Config.objects.first()
    config.google_credentials = credentials_to_json(credentials)
    config.save()

    return redirect(request.session['redirect'])


def deauthorise(request):
    credentials = get_credentials()

    if credentials is not None:
        requests.post('https://accounts.google.com/o/oauth2/revoke',
                      params={'token': credentials.token},
                      headers={'content-type': 'application/x-www-form-urlencoded'})

        config = Config.objects.first()
        config.google_credentials = ""
        config.save()

    return redirect(request.META.get('HTTP_REFERER'))


def credentials_to_json(credentials):
    return json.dumps({'token': credentials.token,
                       'refresh_token': credentials.refresh_token,
                       'token_uri': credentials.token_uri,
                       'client_id': credentials.client_id,
                       'client_secret': credentials.client_secret,
                       'scopes': credentials.scopes})


def get_credentials():
    config = Config.objects.first()
    if not config or not config.google_credentials:
        return None
    try:
        data = json.loads(config.google_credentials)
        return google.oauth2.credentials.Credentials(
            token=data['token'], refresh_token=data['refresh_token'], token_uri=data['token_uri'],
            client_id=data['client_id'], client_secret=data['client_secret'], scopes=data['scopes'])
    except json.JSONDecodeError:
        return None


def insert_booking_to_calendar(booking: Booking):
    creds = get_credentials()
    if creds is not None:
        calendar = googleapiclient.discovery.build(
            API_SERVICE_NAME, API_VERSION, credentials=creds)

        calendar.events().insert(calendarId="primary", conferenceDataVersion=1, body={
            "start": {
                "dateTime": booking.time.isoformat(),
                "timeZone": booking.time.tzname()
            },
            "end": {
                "dateTime": (booking.time + booking.type.length).isoformat(),
                "timeZone": (booking.time + booking.type.length).tzname()
            },
            "summary": str(booking),
            "conferenceData": {},
            "source": {
                "title": "Louise Misell Interiors booking system",
                "url": "https://louisemisellinteriors.co.uk"
            },
            "attendees": [
                {
                    "displayName": f"{booking.customer.first_name} {booking.customer.last_name}",
                    "responseStatus": "accepted",
                    "email": booking.customer.email,
                    "comment": f"Phone: {booking.customer.phone}"
                }
            ],
        }, sendUpdates="all").execute()


def booking_succeeded(booking: Booking):
    config = SiteConfig.objects.first()

    questions_text = []
    for question in booking.booking_question_answers.all():
        questions_text.append(f"{question.question.question}:\r\n{question.answer}")
    questions_text = "\r\n".join(questions_text)

    files_text = []
    for file in booking.booking_files.all():
        files_text.append(f"- {file.file}")
    files_text = "\r\n".join(files_text)

    tz = pytz.timezone(booking.type.timezone)
    time = booking.time.astimezone(tz=tz).strftime("%I:%M%p %a %d %b %Y")
    body = f"Name: {booking.customer.first_name} {booking.customer.last_name}\r\n" \
        f"Email: {booking.customer.email}\r\n" \
        f"Phone: {booking.customer.phone}" \
        f"\r\n\r\n---\r\n\r\n" \
        f"{booking.type.name}\r\n" \
        f"Time: {time}, {booking.type.timezone}\r\n" \
        f"{questions_text}\r\n---\r\n\r\n" \
        f"Files:\r\n" \
        f"{files_text}"
    email_msg = EmailMessage(
        subject=f"{booking.customer.first_name} {booking.customer.last_name} has booked {booking.type.name}",
        body=body,
        to=config.notification_email.split(";"),
        reply_to=[f"{booking.customer.first_name} {booking.customer.last_name} <{booking.customer.email}>"]
    )
    email_msg.send()

    context = {
        "settings": settings,
        "booking_type": booking.type,
        "time": time,
        "first_name": booking.customer.first_name,
        "last_name": booking.customer.last_name,
        "email": booking.customer.email,
        "phone": booking.customer.phone,
        "questions": [{
            "question": q.question,
            "answer": q.answer
        } for q in booking.booking_question_answers.all()]
    }

    email_msg = EmailMultiAlternatives(
        subject=f"Confirmation of your booking with Louise",
        body=render_to_string("bookings/booking_confirmation_txt.html", context),
        to=[booking.customer.email],
        headers={
            "List-Unsubscribe": f"<mailto:{config.email}?subject=unsubscribe>",
        },
        reply_to=[f"Louise Misell <{config.email}>"]
    )
    # email_msg.attach_alternative(render_to_string("bookings/booking_confirmation_amp.html", context), "text/x-amp-html")
    email_msg.attach_alternative(render_to_string("bookings/booking_confirmation.html", context), "text/html")
    email_msg.send()

    insert_booking_to_calendar(booking)


def stripe_webhook(event):
    obj = event.data.object
    if obj.object == "payment_intent":
        booking = Booking.objects.filter(pending=True, stripe_payment_intent_id=obj.id).first()
        if booking:
            if obj.status == "succeeded":
                booking.pending = False
                booking.save()
                booking_succeeded(booking)
