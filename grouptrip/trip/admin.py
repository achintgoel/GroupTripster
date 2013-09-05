from django.contrib import admin
from trip.models import Trip

class TripAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('name',)}
    
admin.site.register(Trip, TripAdmin)