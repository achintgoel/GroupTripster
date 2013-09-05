from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import render_to_string
from django.core import serializers
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.utils.text import slugify
from django.template.defaultfilters import date
from trip.forms import CreateTripForm, CreateActivityForm
from trip.models import Trip, TripParticipants, ActivityItinerary
from tasks.models import Task
from social_auth.db.django_models import UserSocialAuth
import facebook
import datetime
# Create your views here.


def date_range(start_date, end_date):
    if isinstance(start_date, datetime.datetime):
        start_date = start_date.date()
    if isinstance(end_date, datetime.datetime):
        end_date = end_date.date()
    
    # Verify that the start_date comes after the end_date.
    if start_date > end_date:
        raise ValueError('You provided a start_date that comes after the end_date.')
    
    # Jump forward from the start_date...
    while True:
        yield start_date
        # ... one day at a time ...
        start_date = start_date + datetime.timedelta(days=1)
        # ... until you reach the end date.
        if start_date > end_date:
            break
        
@login_required
def save(request):
    form = CreateTripForm(request.POST)
    if form.is_valid():
        user = request.user
    #trip = Trip(name=request.POST.get('name'), slug=slugify(request.POST.get('name')), created_by=user ,start_date=request.POST.get('start_date'), num_days=request.POST.get('num_days'))
        trip = Trip(name=form.cleaned_data['name'], slug=slugify(form.cleaned_data['name']), created_by=user ,start_date=form.cleaned_data['start_date'], end_date=form.cleaned_data['end_date'])
        trip.save()
        
        trip_participant = TripParticipants(trip=trip, participant=user, role=TripParticipants.CREATOR)
        trip_participant.save()

        template = "trip/trip_summary.html"
        html = render_to_string(template, {'trip_info': trip })
        response = simplejson.dumps({'success':'True', 'html': html})
        
    else:
        html = form.errors.as_ul()
        response = simplejson.dumps({'success':'False', 'html': html})
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
    
@login_required
def add_activity(request):
        
    name = request.POST.get('name')
    address = request.POST.get('address')
    description = request.POST.get('description')
    start_date = request.POST.get('start_date')
    start_time = request.POST.get('start_time')
    category = request.POST.get('category')
    reference = request.POST.get('reference')
    slug = request.POST.get('slug')
    #TODO verify user is either creator or planner
    trip = get_object_or_404(Trip, slug=slug)
    form = CreateActivityForm({'name':name, 'address':address, 'reference':reference, 'start_date':start_date,'start_time':start_time, 'category':category, 'description':description})
    #TODO:verify that activity hasnt been added already (by trip id)...if so, get and save the new info
    #TODO: check if form submitted is valid, if not, pass back error to javascript function
    if form.is_valid():
        activity = ActivityItinerary(name=form.cleaned_data['name'], trip=trip, reference=form.cleaned_data['reference'], start_date=form.cleaned_data['start_date'], 
                                     start_time=form.cleaned_data['start_time'], address=form.cleaned_data['address'], category=form.cleaned_data['category'], description=form.cleaned_data['description'])
    
    #activity = ActivityItinerary(trip=trip, name=name, address=address, start_date=start_date, start_time=start_time, category=category, description=description)
    #activity.save() 
        activity.save()
        template = "trip/activity_summary2.html"
        #TODO:is there a better way to figure out which div this activity panel goes into?
        formatted_date = date(activity.start_date, "Y-m-d")
        activities_div_id = "#my%sActivities" % formatted_date
        no_activities_div_id = "#no%sActivities" % formatted_date
        html = render_to_string(template, {'name': activity.name, 'address':activity.address, 'description':activity.description, 'id':activity.id, 'start_time':activity.start_time})
        response = simplejson.dumps({'success':'True', 'html': html, 'activities_div_id':activities_div_id, 'no_activities_div_id':no_activities_div_id})
    
    else:
        html = form.errors.as_ul()
        response = simplejson.dumps({'success':'False', 'html': html})
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')


@login_required
def get_activities(request):
    slug = request.GET.get('slug')
    #TODO make sure user is in this trip
    trip = get_object_or_404(Trip, slug=slug)
    activities = trip.activityitinerary_set.all()
    #TODO consider using serializers everywhere instead of simplejson
    response = serializers.serialize("json", activities, fields=('name', 'reference', 'address'))
    
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
    

def trip_profile(request, slug):
    #TODO:either the trip is created by the user, or user is part of it
    trip = get_object_or_404(Trip, slug=slug)
    #TODO:get only the user objects instead of the TripParticipants objects
    trip_participants = trip.tripparticipants_set.all()
    trip_participants_values = trip.tripparticipants_set.values('participant')
    create_activity_form = CreateActivityForm
    dates = list(date_range(trip.start_date, trip.end_date))
    #TODO:change how this works?!
    #activities is a dictionary with key being date, and value being a list of all activities with that start_date
    activities = {}
    for date in dates:
        activities[date] = trip.activityitinerary_set.filter(start_date=date)
    
    activity_category_icons = ActivityItinerary.ACTIVITY_CATEGORY_ICONS
    
    tasks = Task.objects.filter(trip=trip)
    
    instance = UserSocialAuth.objects.filter(provider='facebook').get(user=request.user)
    graph = facebook.GraphAPI(instance.tokens['access_token'])
    user_profile = graph.get_object("me", fields="id, name, first_name, last_name, picture")
    #friends = graph.get_connections("me", "friends")
    
    #get all social auth profiles of non participant users
    #TODO: move this to an individual function
    users_social_auth = UserSocialAuth.objects.exclude(user__in=trip_participants_values)
    friend_profiles = []
    
    for user_social_auth in users_social_auth:
        friend = graph.get_connections("me", "friends/"+user_social_auth.uid)
        friend_data = friend['data']
        if friend_data:
            friend_profile = graph.get_object(friend_data['id'], fields="id, name, first_name, last_name, picture")
            friend_profiles.append(friend_profile)
    #TODO:change this to get only list of friends
    user_list = User.objects.exclude(pk__in=trip_participants_values)
    return render_to_response('trip/trip_profile.html', locals(), context_instance=RequestContext(request))
