from django.conf import settings
from django.conf.urls.defaults import *
from socialite.apps.linkedin import views

urlpatterns = patterns('',
    url(r'^authenticate/$', views.authenticate, name='linkedin_authenticate'),
    url(r'^authorize/$', views.authorize, name='linkedin_authorize'),
    url(r'^callback/$', views.mediator.callback, name='linkedin_callback'),
)
