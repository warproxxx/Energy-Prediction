from django import forms
from django.contrib.auth import(
    authenticate,
    login,
    logout,
)
import time
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import datetime
from glob import glob
import os

class dashboard_options(forms.Form):

    temp_models = []
    for file in glob('algorithm/models/*'):
        file = os.path.basename(file)
        temp_models.append((file, file))
    models = tuple(temp_models)

    temp_location = []
    for file in glob('algorithm/models/{}/*'.format(temp_models[0][1])):
        file = os.path.basename(file)

        if ("about.json" not in file):
            temp_location.append((file, file))
    locations = tuple(temp_location)

 
    location = forms.ChoiceField(label ="",choices=locations, required=True, initial =0)
    algorithm = forms.ChoiceField(label ="",choices=models, required=True, initial =0)

    loggic_field = forms.CharField(widget=forms.Textarea, required=True)

class algorithm_options(forms.Form):
    buy = forms.CharField(label ="", required=True, max_length =100)


