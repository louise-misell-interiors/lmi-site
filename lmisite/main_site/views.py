import itertools
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from .models import *
from .forms import *
import math
import requests
import json
import bookings.models as booking_models


def index(request):
    slider_imgs = MainSliderImage.objects.all()
    testimonials = Testimonial.objects.filter(featured=True)
    projects = Project.objects.filter(draft=False)[:4]
    services = Service.objects.filter(type=Service.MAIN)
    if not request.user.is_superuser:
        testimonials = testimonials.filter(draft=False)
        services = services.filter(draft=False)
    return render(request, "main_site/index.html",
                  {"testimonials": testimonials, "slider_imgs": slider_imgs, "projects": projects,
                   "services": services})


def config(request):
    return render(request, "main_site/config.js", content_type="application/javascript")


def get_instagram_feed():
    resp = requests.get(f"https://api.instagram.com/v1/users/self/media/recent/?access_token=7175062577.e237e22.5b023451999e42a4ad3477dfc8032d43")
    resp.raise_for_status()
    data = resp.json()
    return data["data"]


def design_insider(request):
    posts = DesignInsiderPost.objects.all()
    if not request.user.is_superuser:
        posts = posts.filter(draft=False)

    short_posts = ShortPost.objects.all()
    if not request.user.is_superuser:
        short_posts = short_posts.filter(draft=False)

    big_post = posts[0]
    posts = posts[1:]
    extra = range((math.ceil(len(posts) / 3) * 3) - len(posts))

    instagram = get_instagram_feed()

    if request.method == "POST":
        form = NewsletterForm(request.POST)
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
                          {"posts": (big_post, posts, extra), "instagram": instagram, "short_posts": short_posts,
                           "form": form, "sent": True})
    else:
        form = NewsletterForm()

    return render(request, "main_site/design_insider.html",
                  {"posts": (big_post, posts, extra), "short_posts": short_posts, "form": form, "instagram": instagram})


def design_insider_post(request, id):
    post = get_object_or_404(DesignInsiderPost, id=id)

    short_posts = ShortPost.objects.all()
    if not request.user.is_superuser:
        short_posts = short_posts.filter(draft=False)

    if request.method == "POST":
        form = NewsletterForm(request.POST)
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
                          {"post": post, "instagram": instagram, "short_posts": short_posts, "form": form, "sent": True})
    else:
        form = NewsletterForm()

    return render(request, "main_site/design_insider_post.html",
                  {"post": post, "instagram": instagram, "short_posts": short_posts, "form": form})


def about(request):
    sections = AboutSection.objects.all()
    if not request.user.is_superuser:
        sections = sections.filter(draft=False)
    return render(request, "main_site/about.html", {"sections": sections})


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
    services = list(itertools.zip_longest(services_m, services_o))
    return render(request, "main_site/services.html", {"services": services})


def testimonials(request):
    testimonials = Testimonial.objects.filter(not_on_testimonials=False)
    if not request.user.is_superuser:
        testimonials = testimonials.filter(draft=False)
    return render(request, "main_site/testimonials.html", {"testimonials": testimonials})


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
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
        form = ContactForm()

    return render(request, "main_site/contact.html", {'form': form, 'sent': False})
