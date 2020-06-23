from django.shortcuts import render, redirect, reverse
from django.conf import settings
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
