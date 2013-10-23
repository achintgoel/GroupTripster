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
from trip.models import Trip, TripParticipants, ActivityItinerary, ActivityComment, ActivityReview
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
    activity_id =  request.POST.get('activity_id')
    name = request.POST.get('name')
    address = request.POST.get('address')
    description = request.POST.get('description')
    start_date = request.POST.get('start_date')
    start_time = request.POST.get('start_time')
    category = request.POST.get('category')
    reference = request.POST.get('reference')
    photo = request.POST.get('photo')
    slug = request.POST.get('slug')

    #TODO verify user is either creator or planner
    
    form = CreateActivityForm({'name':name, 'address':address, 'reference':reference, 'start_date':start_date,'start_time':start_time, 'category':category, 'description':description, 'photo':photo})
    #TODO: check if form submitted is valid, if not, pass back error to javascript function
    
    if form.is_valid():
        if activity_id:
            activity = get_object_or_404(ActivityItinerary, pk=activity_id)
            activity.name = form.cleaned_data['name']
            activity.address = form.cleaned_data['address']
            activity.description = form.cleaned_data['description']
            activity.start_date = form.cleaned_data['start_date']
            activity.start_time = form.cleaned_data['start_time']
            activity.category = form.cleaned_data['category']
            activity.photo = form.cleaned_data['photo']
            edited = 'True'
        else:
            trip = get_object_or_404(Trip, slug=slug)
            activity = ActivityItinerary(name=form.cleaned_data['name'], trip=trip, reference=form.cleaned_data['reference'], start_date=form.cleaned_data['start_date'], 
                                         start_time=form.cleaned_data['start_time'], address=form.cleaned_data['address'], 
                                         category=form.cleaned_data['category'], description=form.cleaned_data['description'], photo=form.cleaned_data['photo'])
            edited = 'False'
            
        activity.save()
        template = "trip/activity_summary2.html"
        #TODO:is there a better way to figure out which div this activity panel goes into?
        formatted_date = date(activity.start_date, "Y-m-d")
        activities_div_id = "#my%sActivities" % formatted_date
        no_activities_div_id = "#no%sActivities" % formatted_date
        html = render_to_string(template, {'activity': activity})
        response = simplejson.dumps({'success':'True', 'html': html, 'activities_div_id':activities_div_id, 'no_activities_div_id':no_activities_div_id, 'edited':edited})
    
    else:
        print(form.errors.as_ul())
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

@login_required
def get_social_activities(request):
    slug = request.GET.get('slug')
    trip = get_object_or_404(Trip, slug=slug)
    #TODO get only activities that your friends were participants in
    trip_activities = trip.activityitinerary_set.values_list('pk', flat=True)
    #TODO:exclude activities that belong to trips that this user was in
    #trips_participated = request.user.trip_participant.values_list('trip', flat=True)
    social_activities = ActivityItinerary.objects.exclude(pk__in=list(trip_activities))
    template = "trip/review_summary.html"
    activities_reviews_info= []
    for social_activity in social_activities:
        activity_reviews = social_activity.activityreview_set.all()
        activity_reviews_info = {}
        activity_reviews_info['name'] = social_activity.name
        activity_reviews_info['address'] = social_activity.address
        activity_reviews_info['reviews'] = []
        for activity_review in activity_reviews:
            instance = UserSocialAuth.objects.filter(provider='facebook').get(user=activity_review.review_by)
            graph = facebook.GraphAPI(instance.tokens['access_token'])
            user_profile = graph.get_object("me", fields="id, name, first_name, last_name, picture")
            html = render_to_string(template, {'activity_review': activity_review, 'reviewer_profile':user_profile})
            activity_reviews_info['reviews'].append(html)
        activities_reviews_info.append(activity_reviews_info)
    
    response = simplejson.dumps({'success':'True', 'activities_reviews_info':activities_reviews_info})      
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')

@login_required
def save_comment(request):
    activity_id = request.POST.get('activity_id')
    comment = request.POST.get('comment')
    comment_by = request.user
    activity = get_object_or_404(ActivityItinerary, pk=activity_id)
    activity_comment = ActivityComment(activity=activity, comment_by=comment_by, comment=comment)
    activity_comment.save()
    
    template = "trip/comment.html"
    instance = UserSocialAuth.objects.filter(provider='facebook').get(user=request.user)
    graph = facebook.GraphAPI(instance.tokens['access_token'])
    user_profile = graph.get_object("me", fields="id, name, first_name, last_name, picture")
    
    html = render_to_string(template, {'activity_comment': activity_comment, 'commentor_profile':user_profile})
    response = simplejson.dumps({'success':'True', 'html':html})
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
    
@login_required
def save_review(request):
    activity_id = request.POST.get('activity_id')
    rating = request.POST.get('rating')
    description = request.POST.get('description')
    review_by = request.user
    activity = get_object_or_404(ActivityItinerary, pk=activity_id)
    activity_review = ActivityReview(activity=activity, rating=rating, description=description, review_by=review_by)
    activity_review.save()
    
    template = "trip/review_summary.html"
    instance = UserSocialAuth.objects.filter(provider='facebook').get(user=request.user)
    graph = facebook.GraphAPI(instance.tokens['access_token'])
    user_profile = graph.get_object("me", fields="id, name, first_name, last_name, picture")
    
    html = render_to_string(template, {'activity_review': activity_review, 'reviewer_profile':user_profile})
    response = simplejson.dumps({'success':'True', 'html':html})
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')

def trip_profile(request, slug):
    #TODO:either the trip is created by the user, or user is part of it
    trip = get_object_or_404(Trip, slug=slug)
    #TODO:get only the user objects instead of the TripParticipants objects
    trip_participants = trip.tripparticipants_set.all()
    trip_participants_values = trip.tripparticipants_set.values_list('participant', flat=True)
    create_activity_form = CreateActivityForm
    dates = list(date_range(trip.start_date, trip.end_date))
    #TODO:change how this works?!
    #activities is a dictionary with key being date, and value being a list of all activities with that start_date
    activities = {}
    activity_itinerary = trip.activityitinerary_set.all()
    for date in dates:
        activities[date] = activity_itinerary.filter(start_date=date)
        
    activity_category_icons = ActivityItinerary.ACTIVITY_CATEGORY_ICONS
    
    tasks = Task.objects.filter(trip=trip)
    
    instance = UserSocialAuth.objects.filter(provider='facebook').get(user=request.user)
    graph = facebook.GraphAPI(instance.tokens['access_token'])
    user_profile = graph.get_object("me", fields="id, name, first_name, last_name, picture")
    
    user_participants_social_pf = {}
    user_non_participants_social_pf = {}
    friends_non_users = []
    friends = graph.get_connections("me", "friends", fields="id, name, first_name, last_name, picture")
    for friend in friends['data']:
        try:
            user_social_auth = UserSocialAuth.objects.get(uid=friend['id'])
            if trip.tripparticipants_set.filter(participant=user_social_auth.user).exists():
                user_participants_social_pf[user_social_auth.user] = friend
            else:
                user_non_participants_social_pf[user_social_auth.user] = friend
        except UserSocialAuth.DoesNotExist:
            friends_non_users.append(friend)
    
    
    
    user_list = User.objects.exclude(pk__in=list(trip_participants_values))
    return render_to_response('trip/trip_profile.html', locals(), context_instance=RequestContext(request))
