from django.db import models
from django.conf import settings
from trip.models import Trip

# Create your models here.
class Task(models.Model):
    ACCOMMODATION = 'accommodation'
    RESERVATION = 'reservation'
    TO_BRING = 'to_bring'
    MISCELLANEOUS = 'miscellaneous'
    TASK_CATEGORY_CHOICES = (
        (ACCOMMODATION, 'Book Accommodation'),
        (RESERVATION, 'Make Reservation'),
        (TO_BRING, 'Bring Item(s)'),
        (MISCELLANEOUS, 'Miscellaneous'),

    )
    
    NEW = 'new'
    COMPLETED = 'completed'
    TASK_STATUS_CHOICES = (
        (NEW, 'New'),
        (COMPLETED, 'Completed'),
    )
    
    trip = models.ForeignKey(Trip)
    name = models.CharField(max_length=500)
    category = models.CharField(max_length=100, choices=TASK_CATEGORY_CHOICES, blank=True)
    description = models.TextField(blank=True)
    link = models.URLField(blank=True)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="task_creator")
    status = models.CharField(max_length=100, choices=TASK_STATUS_CHOICES, default=NEW)
