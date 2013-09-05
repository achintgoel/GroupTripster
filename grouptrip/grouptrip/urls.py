from django.conf.urls import patterns, include, url
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'', include('social_auth.urls')),
    url(r'^accounts/', include('accounts.urls', namespace="accounts")),
    url(r'^trip/', include('trip.urls', namespace="trip")),
    url(r'^invite/', include('invite.urls', namespace="invite")),
    url(r'^finder/', include('finder.urls', namespace="finder")),
    url(r'^tasks/', include('tasks.urls', namespace="tasks")),
    # Examples:
    # url(r'^$', 'socialecom.views.home', name='home'),
    # url(r'^socialecom/', include('socialecom.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
