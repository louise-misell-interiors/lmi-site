from django.urls import path
from django.contrib.sitemaps.views import sitemap
from . import views
from .sitemap import SITEMAP

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('project/<id>/', views.project, name='project'),
    path('services/', views.services, name='services'),
    path('online_design/', views.online_design, name='online_design'),
    path('design_insider/', views.design_insider, name='design_insider'),
    path('design_insider.rss', views.DesignInsiderFeed(), name='design_insider_rss'),
    path('design_insider/<id>/', views.design_insider_post, name='design_insider_post'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('contact/', views.contact, name='contact'),
    path('booking/<id>', views.booking, name='booking'),
    path('config.js', views.config, name='config.js'),

    path('facebook/authorise/', views.fb_authorise, name='fb_authorise'),
    path('facebook/oauth/', views.fb_oauth, name='fb_oauth'),
    path('facebook/deauth/', views.fb_deauthorise, name='fb_deauthorise'),

    path('mailchimp/authorise/', views.newsletter_authorise, name='newsletter_authorise'),
    path('mailchimp/oauth/', views.newsletter_oauth, name='newsletter_oauth'),
    path('mailchimp/deauth/', views.newsletter_deauthorise, name='newsletter_deauthorise'),


    path('404', views.page_not_found),


    path('sitemap.xml', sitemap,  {'sitemaps': SITEMAP, 'template_name': 'main_site/sitemap.xml'},
         name='django.contrib.sitemaps.views.sitemap')
]

