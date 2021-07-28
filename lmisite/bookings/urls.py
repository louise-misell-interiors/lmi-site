from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload_file, name='upload-file'),
    path('authorise', views.authorise, name='authorise'),
    path('deauthorise', views.deauthorise, name='deauthorise'),
    path('oauth', views.oauth, name='oauth'),
]

app_name = 'bookings'
