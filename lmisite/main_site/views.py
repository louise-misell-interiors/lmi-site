import itertools
from django.shortcuts import render, get_object_or_404
from .models import *


def index(request):
    slider_imgs = MainSliderImage.objects.all()
    testimonials = Testimonial.objects.filter(featured=True)
    projects = Project.objects.all()[:4]
    services = Service.objects.filter(type=Service.MAIN)
    return render(request, "main_site/index.html",
                  {"testimonials": testimonials, "slider_imgs": slider_imgs, "projects": projects,
                   "services": services})


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
    return render(request, "main_site/contact.html")
