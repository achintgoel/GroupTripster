from django import forms
from django.forms import ModelForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field
from django.contrib.admin import widgets
from tasks.models import Task

class TaskForm(ModelForm):
    class Meta:
        model = Task
        exclude = ('trip', 'created_by', 'assigned_to', 'status')
    
    def __init__(self, *args, **kwargs):
        self.helper = FormHelper()
        super(TaskForm, self).__init__(*args, **kwargs)

