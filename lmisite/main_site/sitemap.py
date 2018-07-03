from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import *


class ProjectSitemap(Sitemap):
    def items(self):
        return Project.objects.all()

    def location(self, obj):
        return reverse('project', kwargs={'id': obj.id})


class StaticViewSitemap(Sitemap):
    def items(self):
        return ['about', 'testimonials', 'portfolio', 'services', 'contact']

    def location(self, item):
        return reverse(item)


SITEMAP = {
    "projects": ProjectSitemap,
    "static": StaticViewSitemap,
}
