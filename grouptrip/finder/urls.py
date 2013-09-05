from django.conf.urls import patterns, url
from finder import views
urlpatterns = patterns('',
    url(r'^get_finder_results/$', views.get_finder_results , name='get_finder_results'),

)

