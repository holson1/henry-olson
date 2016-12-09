from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^api/$', views.bart_api_request, name='index')
]