from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about', views.about, name='about'),
    path('portfolio', views.portfolio, name='portfolio'),
    path('project/<id>', views.project, name='project'),
    path('services', views.services, name='services'),
    path('testimonials', views.testimonials, name='testimonials'),
    path('contact', views.contact, name='contact'),
]
