from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.bart_landing, name='index'),
    url(r'^api/$', views.bart_api_request, name='api_root')
]