from django.urls import path
from django.contrib.sitemaps.views import sitemap
from . import views
from .sitemap import SITEMAP

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('project/<id>', views.project, name='project'),
    path('services', views.services, name='services'),
    path('testimonials', views.testimonials, name='testimonials'),
    path('contact', views.contact, name='contact'),


    path('sitemap.xml', sitemap, {'sitemaps': SITEMAP}, name='django.contrib.sitemaps.views.sitemap')
]
