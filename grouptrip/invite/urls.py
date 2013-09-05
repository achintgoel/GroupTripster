from django.conf.urls import patterns, url
from invite import views

urlpatterns = patterns('',
    url(r'^send_invite/$', views.send_invite, name='send_invite'),
    url(r'^accept_invite/(?P<slug>[-\w]+)/$', views.accept_invite, name='accept_invite'),

)

