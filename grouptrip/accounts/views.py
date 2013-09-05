from django.shortcuts import render, render_to_response
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from trip.forms import CreateTripForm
from trip.models import Trip
from invite.models import TripInvitations
from social_auth.db.django_models import UserSocialAuth
import facebook
# Create your views here.

 
def register(request):
    """ view displaying customer registration form """
    if request.method == 'POST':
        postdata = request.POST.copy()
        form = UserCreationForm(postdata)
        if form.is_valid():
            #form.save()
            user = form.save(commit=False)  # new
            user.save()  # new
            un = postdata.get('username','')
            pw = postdata.get('password1','')
            new_user = authenticate(username=un, password=pw)
            if new_user and new_user.is_active:
                login(request, new_user)
                url = reverse('accounts:profile')
                return HttpResponseRedirect(url)
    else:
        #TODO: already logged in case
        form = UserCreationForm()
    page_title = 'User Registration'
    return render_to_response('registration/create_user.html', locals(), context_instance=RequestContext(request))

@login_required
def profile(request):
    user = request.user
    create_trip_form = CreateTripForm
    #Get all trips created by this user
    #trips = user.created_by.all()
    
    participating_trips = user.trip_participant.all()
    pending_invitations = user.invitation_recipient.filter(status=TripInvitations.INVITED)
    
    instance = UserSocialAuth.objects.filter(provider='facebook').get(user=request.user)
    graph = facebook.GraphAPI(instance.tokens['access_token'])
    user_profile = graph.get_object("me", fields="id, name, first_name, last_name, picture")
    
    return render_to_response('accounts/profile.html', locals(), context_instance=RequestContext(request))