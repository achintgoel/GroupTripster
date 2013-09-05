from django.conf.urls import patterns, url
from accounts import views

urlpatterns = patterns('',
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout_then_login', name='logout_then_login'),
    url(r'^register/$', views.register, name='register'),
)