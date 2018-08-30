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

class algorithm_options(forms.Form):
    starting_cash = forms.IntegerField(min_value=0, required = True)
    comission_percentage = forms.CharField(label ="", required=True, max_length =10)
    test_type = forms.CharField(widget=forms.HiddenInput(), required=True,  max_length =10)
    #strategies=(('s1','Maximizing Return (Aggressive but risky)'),('s2','Minimizing Risk'),('s3','Maximizing Sharpe ratio'), ('s4','Maximizing sortino ratio'))
    strategies=(('s1','Normal'), ('s2', 'Aggressive'))
    strategy_type = forms.ChoiceField(label ="",choices=strategies, required=True, initial =0)


