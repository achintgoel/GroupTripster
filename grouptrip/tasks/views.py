from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core import serializers
from django.core import urlresolvers
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.utils.text import slugify
from django.template.defaultfilters import date
from tasks.forms import TaskForm
from tasks.models import Task
from trip.models import Trip

@login_required
def task_form(request):
    template = "tasks/task_form.html"
    html = render_to_string(template)
    response = simplejson.dumps({'success':'True', 'html': html})
    
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')

@login_required
def complete_task(request):
    task_id = request.POST.get('task_id')
    slug = request.POST.get('slug')
    trip = get_object_or_404(Trip, slug=slug)
    task = get_object_or_404(Task, id=task_id, trip=trip, assigned_to=request.user)
    task.status = Task.COMPLETED
    task.save()
    #TODO Might want to not 404?
    response = simplejson.dumps({'success':'True'})
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')

@login_required
def save_task(request):
    name = request.POST.get('name')
    description = request.POST.get('description')
    category = request.POST.get('category')
    link = request.POST.get('link')
    assign_to = request.POST.get('assign_to')
    slug = request.POST.get('slug')
    #TODO verify user is either creator or planner
    trip = get_object_or_404(Trip, slug=slug)
    form = TaskForm({'name':name, 'link':link, 'category':category, 'description':description})
    #TODO:verify that task hasnt been added already (by task id)...if so, get and save the new info
    #TODO: check if form submitted is valid, if not, pass back error to javascript function
    if form.is_valid():
        #TODO:check if the assigned_to user is a valid user
        assign_to_user = User.objects.get(username=assign_to)
        task = Task(name=form.cleaned_data['name'], trip=trip, category=form.cleaned_data['category'], link=form.cleaned_data['link'], description=form.cleaned_data['description'], created_by=request.user, assigned_to=assign_to_user, status=Task.NEW)
    
    #activity = ActivityItinerary(trip=trip, name=name, address=address, start_date=start_date, start_time=start_time, category=category, description=description)
    #activity.save() 
        task.save()
        template = "tasks/task_summary.html"
        html = render_to_string(template, {'task':task})
        response = simplejson.dumps({'success':'True', 'html': html})
    
    else:
        html = form.errors.as_ul()
        response = simplejson.dumps({'success':'False', 'html': html})
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')

