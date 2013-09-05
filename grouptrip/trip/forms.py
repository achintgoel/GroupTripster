from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field
from django.contrib.admin import widgets
from trip.models import Trip, ActivityItinerary

class CreateTripForm(ModelForm):
    class Meta:
        model = Trip
        exclude = ('slug','created_by')
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        super(CreateTripForm, self).__init__(*args, **kwargs)
        self.helper.form_class = 'form-horizontal'

class CreateActivityForm(ModelForm):
    class Meta:
        model = ActivityItinerary
        exclude = ('trip')
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        super(CreateActivityForm, self).__init__(*args, **kwargs)
        