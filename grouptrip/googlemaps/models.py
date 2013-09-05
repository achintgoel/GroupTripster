from django.db import models
from django.conf import settings

# Create your models here.
class Activity(models.Model):
    name = models.CharField(max_length=50)
    formatted_address = models.CharField(max_length=200)
    longitude = models.FloatField()
    latitude = models.FloatField()
    description = models.TextField()
    
    def __unicode__(self):
        return self.name