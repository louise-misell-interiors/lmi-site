from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('authorise', views.authorise, name='authorise'),
    path('deauthorise', views.deauthorise, name='deauthorise'),
    path('oauth', views.oauth, name='oauth'),
    path('graphql', csrf_exempt(views.SentryGraphQLView.as_view(graphiql=True))),
]

app_name = 'bookings'
