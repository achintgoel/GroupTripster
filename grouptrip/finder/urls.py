from django.conf.urls import patterns, url
from finder import views
urlpatterns = patterns('',
    url(r'^get_finder_results/$', views.get_finder_results , name='get_finder_results'),
    url(r'^get_finder_results_yelp/$', views.get_finder_results_yelp , name='get_finder_results_yelp'),
    url(r'^get_finder_results_expedia/$', views.get_finder_results_expedia , name='get_finder_results_expedia'),

)

