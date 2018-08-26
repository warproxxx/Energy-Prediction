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

class dashboard_options(forms.Form):
    temp_models = []
    for file in glob('algorithm/models/*'):
        file = file.replace('algorithm/models\\', '')
        temp_models.append((file, file))
    models = tuple(temp_models)

    temp_location = []
    for file in glob('algorithm/models/tri_model_15_minute/*'):
        file = file.replace('algorithm/models/tri_model_15_minute\\', '')
        temp_location.append((file, file))
    locations = tuple(temp_location)
 
    location = forms.ChoiceField(label ="",choices=locations, required=True)
    algorithm = forms.ChoiceField(label ="",choices=models, required=True)

    buy = forms.IntegerField(label='',
                                         min_value=1,
                                         max_value=99,
                                         required=False)

    sell = forms.IntegerField(label='   ',
                                         min_value=1,
                                         max_value=99,
                                         required=False)




