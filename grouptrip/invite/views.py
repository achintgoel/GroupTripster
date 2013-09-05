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
from trip.forms import CreateTripForm, CreateActivityForm
from trip.models import Trip, TripParticipants, ActivityItinerary
from invite.models import TripInvitations
from social_auth.db.django_models import UserSocialAuth
import facebook
import datetime

@login_required
def send_invite(request):
    user_pk = request.POST.get('user_pk')
    slug = request.POST.get('slug')
    #TODO:verify that the user_pk is in the friends list for this user
    trip = get_object_or_404(Trip, slug=slug, created_by=request.user)
    recipient = User.objects.get(pk=user_pk)
    #TODO:verify that this user hasnt already been sent an invite
    invitation = TripInvitations(trip=trip, sender=request.user, recipient=recipient)
    invitation.save();
    
    response = simplejson.dumps({'success':'True'})
    
    return HttpResponse(response, 
                        content_type='application/javascript; charset=utf-8')
    

@login_required
def accept_invite(request, slug):
    user = request.user
    trip = get_object_or_404(Trip, slug=slug)
    trip_invitation = get_object_or_404(TripInvitations, recipient=user, trip=trip)
    trip_invitation.status = TripInvitations.ACCEPTED
    trip_invitation.save()
    #TODO:change this to include the role
    trip_participant = TripParticipants(trip=trip, participant=user, role=TripParticipants.VIEWER)
    trip_participant.save()
    url = urlresolvers.reverse('trip:profile', kwargs={'slug': trip.slug})
    return HttpResponseRedirect(url)
    
    