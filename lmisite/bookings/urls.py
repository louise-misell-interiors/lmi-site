from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('upload', views.upload_file, name='upload-file'),
    path('authorise', views.authorise, name='authorise'),
    path('deauthorise', views.deauthorise, name='deauthorise'),
    path('oauth', views.oauth, name='oauth'),
    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True))),
    path('stripe_webhook/', csrf_exempt(views.stripe_webhook)),
]

app_name = 'bookings'
