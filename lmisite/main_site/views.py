import itertools
from django.core.mail import send_mail
from django.shortcuts import render, get_object_or_404
from .models import *
from .forms import *
import bookings.models as booking_models


def index(request):
    slider_imgs = MainSliderImage.objects.all()
    testimonials = Testimonial.objects.filter(featured=True)
    projects = Project.objects.all()[:4]
    services = Service.objects.filter(type=Service.MAIN)
    return render(request, "main_site/index.html",
                  {"testimonials": testimonials, "slider_imgs": slider_imgs, "projects": projects,
                   "services": services})


def design_insider(request):
    posts = DesignInsiderPost.objects.all()[:15]

    posts1 = posts[0::3]
    posts2 = posts[1::3]
    posts3 = posts[2::3]
    return render(request, "main_site/design_insider.html", {"posts": (posts1, posts2, posts3)})


def design_insider_post(request, id):
    post = get_object_or_404(DesignInsiderPost, id=id)
    return render(request, "main_site/design_insider_post.html", {"post": post})


def about(request):
    sections = AboutSection.objects.all()
    return render(request, "main_site/about.html", {"sections": sections})


def portfolio(request):
    projects = Project.objects.all()
    return render(request, "main_site/portfolio.html", {"projects": projects})


def project(request, id):
    project = get_object_or_404(Project, id=id)
    return render(request, "main_site/project.html", {"project": project})


def services(request):
    services_m = Service.objects.filter(type=Service.MAIN)
    services_o = Service.objects.filter(type=Service.OTHER)
    services = list(itertools.zip_longest(services_m, services_o))
    return render(request, "main_site/services.html", {"services": services})


def testimonials(request):
    testimonials = Testimonial.objects.filter(not_on_testimonials=False)
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

    return render(request, "main_site/contact.html", {'form': form, 'sent': False })
