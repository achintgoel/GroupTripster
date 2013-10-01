from django.db import models
from django.conf import settings

# Create your models here.
class Trip(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=255, unique=True,
                            help_text='Unique value for trip page URL, created automatically from name.')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_by")
    start_date = models.DateField("Start Date")
    end_date = models.DateField("End Date")
    
    class Meta:
        ordering = ['start_date']
    
    def __unicode__(self):
        return self.name
    
    @models.permalink
    def get_absolute_url(self):
        return ('trip:profile', (), { 'slug': self.slug })


class TripParticipants(models.Model):
    CREATOR = 'creator'
    VIEWER = 'viewer'
    PLANNER = 'planner'
    ROLE_CHOICES = (
        (CREATOR, 'Creator'),
        (VIEWER, 'Viewer'),
        (PLANNER, 'Planner'),
    )
    trip = models.ForeignKey(Trip)
    participant = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="trip_participant")
    role = models.CharField(max_length=100, choices=ROLE_CHOICES, default=VIEWER)

class ActivityItinerary(models.Model):
    RESTAURANT = 'restaurant'
    BAR_CLUB = 'bar_club'
    CONCERT = 'concert'
    ATTRACTION = 'attraction'
    ACTIVITY_CATEGORY_CHOICES = (
        (RESTAURANT, 'Restaurant'),
        (BAR_CLUB, 'Bar/Club'),
        (CONCERT, 'Concert'),
        (ATTRACTION, 'Attraction'),
    )
    
    ACTIVITY_CATEGORY_ICONS = {RESTAURANT:'glyphicon glyphicon-cutlery', 
                               BAR_CLUB:'glyphicon glyphicon-glass', 
                               CONCERT:'glyphicon glyphicon-music', 
                               ATTRACTION:'glyphicon glyphicon-map-marker', '':'glyphicon glyphicon-question-sign'}
    
    trip = models.ForeignKey(Trip)
    name = models.CharField(max_length=500)
    address = models.CharField(max_length=500, blank=True)
    reference = models.CharField(max_length=1000, blank=True)
    start_date = models.DateField("Date", blank=True, null=True)
    start_time = models.TimeField("Time",blank=True, null=True)
    category = models.CharField(max_length=100, choices=ACTIVITY_CATEGORY_CHOICES, blank=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['start_date', 'start_time']

class ActivityComment(models.Model):
    activity = models.ForeignKey(ActivityItinerary)
    comment_by =  models.ForeignKey(settings.AUTH_USER_MODEL)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
