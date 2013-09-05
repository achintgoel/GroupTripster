from django.conf.urls import patterns, url
from tasks import views

urlpatterns = patterns('',
    url(r'^task_form/$', views.task_form, name='task_form'),
    url(r'^save_task/$', views.save_task, name='save_task'),
    url(r'^complete_task/$', views.complete_task, name='complete_task'),

)

