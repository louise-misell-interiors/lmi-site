import itertools
import google_auth_oauthlib.flow
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.conf import settings
from .models import *
from . import forms
import math
import requests
import json
import bookings.models as booking_models

CLIENT_SECRETS_FILE = "facebook_client_secret.json"
SCOPES = ['instagram_basic', 'pages_show_list']


def index(request):
    slider_imgs = MainSliderImage.objects.all()
    testimonials = Testimonial.objects.filter(featured=True)
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


def design_insider(request):
    posts = DesignInsiderPost.objects.all()
    if not request.user.is_superuser:
        posts = posts.filter(draft=False)

    short_posts = ShortPost.objects.all()
    if not request.user.is_superuser:
        short_posts = short_posts.filter(draft=False)

    if request.method == "POST":
        form = forms.NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']

            matching_entries = NewsletterEntry.objects.filter(email=email)
            if len(matching_entries) == 0:
                entry = NewsletterEntry()
                entry.email = email
                entry.name = name
                entry.save()

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
        form = forms.NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            name = form.cleaned_data['name']

            matching_entries = NewsletterEntry.objects.filter(email=email)
            if len(matching_entries) == 0:
                entry = NewsletterEntry()
                entry.email = email
                entry.name = name
                entry.save()

            return render(request, "main_site/design_insider_post.html",
                          {"post": post, "short_posts": short_posts, "form": form, "sent": True})
    else:
        form = forms.NewsletterForm()

    return render(request, "main_site/design_insider_post.html",
                  {"post": post, "short_posts": short_posts, "form": form})


def about(request):
    sections = AboutSection.objects.all()
    testimonials = Testimonial.objects.filter(featured=True)
    if not request.user.is_superuser:
        sections = sections.filter(draft=False)
        testimonials = testimonials.filter(draft=False)
    return render(request, "main_site/about.html", {"sections": sections, "testimonial": testimonials.first()})


def portfolio(request):
    projects = Project.objects.all()
    if not request.user.is_superuser:
        projects = projects.filter(draft=False)
    return render(request, "main_site/portfolio.html", {"projects": projects})


def project(request, id):
    project = get_object_or_404(Project, id=id)
    return render(request, "main_site/project.html", {"project": project})


def services(request):
    services_m = Service.objects.filter(type=Service.MAIN)
    services_o = Service.objects.filter(type=Service.OTHER)
    if not request.user.is_superuser:
        services_m = services_m.filter(draft=False)
        services_o = services_o.filter(draft=False)
    services = list(itertools.chain(services_m, services_o))
    return render(request, "main_site/services.html", {"services": services})


def testimonials(request):
    testimonials = Testimonial.objects.filter(not_on_testimonials=False)
    if not request.user.is_superuser:
        testimonials = testimonials.filter(draft=False)
    return render(request, "main_site/testimonials.html", {"testimonials": testimonials})


def contact(request):
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

            return render(request, "main_site/contact.html", {'form': form, 'sent': True})
    else:
        form = forms.ContactForm()

    return render(request, "main_site/contact.html", {'form': form, 'sent': False})


def authorise(request):
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)

    uri = request.build_absolute_uri(reverse('oauth'))
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
    uri = request.build_absolute_uri(reverse('oauth'))
    if not settings.DEBUG:
        uri = uri.replace("http://", "https://")
    flow.redirect_uri = uri

    token = flow.fetch_token(code=request.GET.get("code"))

    config = SiteConfig.objects.first()
    config.facebook_token = credentials_to_json(token)
    config.save()

    return redirect(request.session['redirect'])


def deauthorise(request):
    credentials = get_credentials()

    if credentials is not None:
        requests.delete('https://graph.facebook.com/v3.3/{user-id}/permissions',
                        params={'access_token': credentials})

        config = SiteConfig.objects.first()
        config.facebook_token = ""
        config.save()

    return redirect(request.META.get('HTTP_REFERER'))


def credentials_to_json(credentials):
    return json.dumps({'token': credentials['access_token']})


def get_credentials():
    config = SiteConfig.objects.first()
    try:
        data = json.loads(config.facebook_token)
        return data['token']
    except json.JSONDecodeError:
        return None
