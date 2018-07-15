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
    path('design_insider', views.design_insider, name='design_insider'),
    path('design_insider/<id>', views.design_insider_post, name='design_insider_post'),
    path('testimonials', views.testimonials, name='testimonials'),
    path('contact', views.contact, name='contact'),


    path('sitemap.xml', sitemap,  {'sitemaps': SITEMAP,'template_name': 'main_site/sitemap.xml'},
         name='django.contrib.sitemaps.views.sitemap')
]

