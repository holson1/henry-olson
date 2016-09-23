from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.bart_api_request, name='index')
]