import itertools
import google_auth_oauthlib.flow
import google.oauth2.credentials
import googleapiclient.discovery
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.conf import settings
from .models import *
from . import forms
import requests
import json
import bookings.models as booking_models
from django.db.models import Q

FB_CLIENT_SECRETS_FILE = "facebook_client_secret.json"
FB_SCOPES = ['instagram_basic', 'pages_show_list']
NEWSLETTER_CLIENT_SECRETS_FILE = "newsletter_client_secret.json"
NEWSLETTER_SCOPES = ['https://www.googleapis.com/auth/admin.directory.group.member',
                     'https://www.googleapis.com/auth/admin.directory.group.readonly']
NEWSLETTER_API_SERVICE_NAME = 'admin'
NEWSLETTER_API_VERSION = 'directory_v1'


def index(request):
    slider_imgs = MainSliderImage.objects.all()
    testimonials = Testimonial.objects.filter(featured_on=Testimonial.HOME_PAGE)
    projects = Project.objects.filter(draft=False)[:4]
    services = Service.objects.filter(type=Service.MAIN)
    if not request.user.is_superuser:
        testimonials = testimonials.filter(draft=False)
        services = services.filter(draft=False)
    return render(request, "main_site/index.html",
                  {"testimonial": testimonials.first(), "slider_imgs": slider_imgs, "projects": projects,
                   "services": services})


def config(request):
    return render(request, "main_site/config.js", content_type="application/javascript")


def handle_newsletter(request):
    form = forms.NewsletterForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data['email']
        name = form.cleaned_data['name']

        config = SiteConfig.objects.first()
        creds = get_newsletter_credentials()
        directory = googleapiclient.discovery.build(NEWSLETTER_API_SERVICE_NAME, NEWSLETTER_API_VERSION,
                                                    credentials=creds)

        members_resp = directory.members().list(groupKey=config.newsletter_group_id, includeDerivedMembership=False)\
            .execute()
        members = members_resp.get('members', [])
        while members_resp.get("nextPageToken") is not None:
            members_resp = directory.members()\
                .list(groupKey=config.newsletter_group_id, includeDerivedMembership=False,
                      pageToken=members_resp.get("nextPageToken"))\
                .execute()
            members.extend(members_resp.get('members', []))

        if email in map(lambda m: m["email"], members):
            return form
        member = directory.members().insert(groupKey=config.newsletter_group_id, body={
            "delivery_settings": "ALL_MAIL",
            "role": "MEMBER",
            "email": email
        }).execute()

        entry = NewsletterEntry()
        entry.name = name
        entry.google_id = member.get("id", "")
        entry.save()
    return form


def design_insider(request):
    posts = DesignInsiderPost.objects.all()
    if not request.user.is_superuser:
        posts = posts.filter(draft=False)

    short_posts = ShortPost.objects.all()
    if not request.user.is_superuser:
        short_posts = short_posts.filter(draft=False)

    if request.method == "POST":
        form = handle_newsletter(request)
        return render(request, "main_site/design_insider.html",
                      {"posts": posts, "short_posts": short_posts, "form": form, "sent": True})
    else:
        form = forms.NewsletterForm()

    return render(request, "main_site/design_insider.html",
                  {"posts": posts, "short_posts": short_posts, "form": form})


def design_insider_post(request, id):
    post = get_object_or_404(DesignInsiderPost, id=id)

    short_posts = ShortPost.objects.all()
    if not request.user.is_superuser:
        short_posts = short_posts.filter(draft=False)

    if request.method == "POST":
        form = handle_newsletter(request)
        return render(request, "main_site/design_insider_post.html",
                      {"post": post, "short_posts": short_posts, "form": form, "sent": True})
    else:
        form = forms.NewsletterForm()

    return render(request, "main_site/design_insider_post.html",
                  {"post": post, "short_posts": short_posts, "form": form})


def about(request):
    testimonials = Testimonial.objects.filter(featured_on=Testimonial.ABOUT_PAGE)
    if not request.user.is_superuser:
        testimonials = testimonials.filter(draft=False)
    return render(request, "main_site/about.html", {"testimonial": testimonials.first()})


def portfolio(request):
    projects = Project.objects.all()
    if not request.user.is_superuser:
        projects = projects.filter(draft=False)
    return render(request, "main_site/portfolio.html", {"projects": projects})


def project(request, id):
    project = get_object_or_404(Project, id=id)
    projects = Project.objects.filter(~Q(id=id))
    if not request.user.is_superuser:
        projects = projects.filter(draft=False)
    return render(request, "main_site/project.html", {"project": project, "projects": projects})


def services(request):
    services_m = Service.objects.filter(type=Service.MAIN)
    services_o = Service.objects.filter(type=Service.OTHER)
    testimonials = Testimonial.objects.filter(featured_on=Testimonial.SERVICES_PAGE)
    if not request.user.is_superuser:
        services_m = services_m.filter(draft=False)
        services_o = services_o.filter(draft=False)
        testimonials = testimonials.filter(draft=False)
    services = list(itertools.chain(services_m, services_o))
    return render(request, "main_site/services.html", {"services": services, "testimonial": testimonials.first()})


def testimonials(request):
    testimonials = Testimonial.objects.filter(not_on_testimonials=False)
    if not request.user.is_superuser:
        testimonials = testimonials.filter(draft=False)
    return render(request, "main_site/testimonials.html", {"testimonials": testimonials})


def contact(request):
    testimonials = Testimonial.objects.filter(featured_on=Testimonial.CONTACT_PAGE)
    if not request.user.is_superuser:
        testimonials = testimonials.filter(draft=False)

    if request.method == 'POST':
        form = forms.ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['your_name']
            email = form.cleaned_data['your_email']
            phone = form.cleaned_data['your_phone']
            message = form.cleaned_data['message']

            subject = f"{name} has sent a message on your website"
            body = f"Name: {name}\r\nEmail: {email}\r\nPhone: {phone}\r\n\r\n---\r\n\r\n{message}"

            config = SiteConfig.objects.first()
            recipients = [config.email]
            send_mail(subject, body, email, recipients)

            matching_customers = booking_models.Customer.objects.filter(email=email)
            if len(matching_customers) > 0:
                customer = matching_customers.first()
            else:
                customer = booking_models.Customer()
                customer.email = email
            customer.name = name
            customer.phone = phone

            customer.full_clean()
            customer.save()

            return render(request, "main_site/contact.html", {'form': form, 'sent': True, "testimonial": testimonials.first()})
    else:
        form = forms.ContactForm()

    return render(request, "main_site/contact.html", {'form': form, 'sent': False, "testimonial": testimonials.first()})


def fb_authorise(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        FB_CLIENT_SECRETS_FILE, scopes=FB_SCOPES)

    uri = request.build_absolute_uri(reverse('fb_oauth'))
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


def fb_oauth(request):
    state = request.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        FB_CLIENT_SECRETS_FILE, scopes=FB_SCOPES, state=state)
    uri = request.build_absolute_uri(reverse('fb_oauth'))
    if not settings.DEBUG:
        uri = uri.replace("http://", "https://")
    flow.redirect_uri = uri

    token = flow.fetch_token(code=request.GET.get("code"))

    config = SiteConfig.objects.first()
    config.facebook_token = fb_credentials_to_json(token)
    config.save()

    return redirect(request.session['redirect'])


def fb_deauthorise(request):
    credentials = get_fb_credentials()

    if credentials is not None:
        requests.delete('https://graph.facebook.com/v3.3/{user-id}/permissions',
                        params={'access_token': credentials})

        config = SiteConfig.objects.first()
        config.facebook_token = ""
        config.save()

    return redirect(request.META.get('HTTP_REFERER'))


def fb_credentials_to_json(credentials):
    return json.dumps({'token': credentials['access_token']})


def get_fb_credentials():
    config = SiteConfig.objects.first()
    if config is None:
        return None
    try:
        data = json.loads(config.facebook_token)
        return data['token']
    except json.JSONDecodeError:
        return None


def newsletter_authorise(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        NEWSLETTER_CLIENT_SECRETS_FILE, scopes=NEWSLETTER_SCOPES)

    uri = request.build_absolute_uri(reverse('newsletter_oauth'))
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


def newsletter_oauth(request):
    state = request.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        NEWSLETTER_CLIENT_SECRETS_FILE, scopes=NEWSLETTER_SCOPES, state=state)
    uri = request.build_absolute_uri(reverse('newsletter_oauth'))
    if not settings.DEBUG:
        uri = uri.replace("http://", "https://")
    flow.redirect_uri = uri

    flow.fetch_token(code=request.GET.get("code"))

    credentials = flow.credentials
    config = SiteConfig.objects.first()
    config.newsletter_credentials = newsletter_credentials_to_json(credentials)
    config.save()

    return redirect(request.session['redirect'])


def newsletter_deauthorise(request):
    credentials = get_newsletter_credentials()

    if credentials is not None:
        requests.post('https://accounts.google.com/o/oauth2/revoke',
                      params={'token': credentials.token},
                      headers={'content-type': 'application/x-www-form-urlencoded'})

        config = SiteConfig.objects.first()
        config.newsletter_credentials = ""
        config.save()

    return redirect(request.META.get('HTTP_REFERER'))


def newsletter_credentials_to_json(credentials):
    return json.dumps({'token': credentials.token,
                       'refresh_token': credentials.refresh_token,
                       'token_uri': credentials.token_uri,
                       'client_id': credentials.client_id,
                       'client_secret': credentials.client_secret,
                       'scopes': credentials.scopes})


def get_newsletter_credentials():
    config = SiteConfig.objects.first()
    if config is None:
        return None
    try:
        data = json.loads(config.newsletter_credentials)
        return google.oauth2.credentials.Credentials(
            token=data['token'], refresh_token=data['refresh_token'], token_uri=data['token_uri'],
            client_id=data['client_id'], client_secret=data['client_secret'], scopes=data['scopes'])
    except json.JSONDecodeError:
        return None