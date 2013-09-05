from django.db import models
from django.conf import settings
from trip.models import Trip
# Create your models here.
class TripInvitations(models.Model):
    INVITED = 'invited'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'
    INVITATION_STATUS_CHOICES = (
        (INVITED, 'invited'),
        (ACCEPTED, 'accepted'),
        (DECLINED, 'declined'),
    )
    
    trip = models.ForeignKey(Trip, related_name="trip_invitations")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="invitation_sender")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="invitation_recipient")
    status = models.CharField(max_length=100, choices=INVITATION_STATUS_CHOICES, default=INVITED)