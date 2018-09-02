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
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

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
    starting_cash = forms.IntegerField(min_value=0, required = True, initial=10000)
    #comission_percentage = forms.FloatField(required=True, min_value = 0, initial=0.1)
    test_type = forms.CharField(widget=forms.HiddenInput(), required=True,  max_length =10)
    strategies=(('s1','Normal'), ('s2', 'Aggressive'))
    strategy_type = forms.ChoiceField(label ="",choices=strategies, required=True, initial =0)


class userLoginForm(forms.Form):
    username = forms.CharField(max_length = 20, label ="*Your Username or Email")
    password = forms.CharField(widget = forms.PasswordInput, label ="*Your Password")
    
    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        user = authenticate(username=username, password =password)
        if not user:
            raise forms.ValidationError("Incorrect username or password")
        elif not user.is_active:
            raise forms.ValidationError("This user is no longer active.")
        return super(userLoginForm, self).clean(*args, **kwargs)

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "username","email", "password1", "password2")
        
    def clean_email(self):
        email1 = self.cleaned_data['email']
        if User.objects.filter(email=email1).exists():
            raise forms.ValidationError('This email address is already in use.')
        else:
            return email1
        

    def clean_password2(self):
        password1 = self.cleaned_data['password1']
        password2 = self.cleaned_data['password2']
        if password1 != password2:
            raise forms.ValidationError("Password doesnot matches.")
        return password2

    def save(self, datas):
        u = User.objects.create_user(datas['first_name'],
                                     datas['last_name'],
                                     datas['username'],
                                     datas['email'],
                                     datas['password1'])
        u.save()
        user_profile=profile()
        user_profile.user=u
        user_profile.verified=False
        user_profile.activation_key=datas['activation_key']
        user_profile.m_plans = datas['m_plans']
        user_profile.m_time = datas['m_time']
        fullName = datas['first_name'] + " " + datas['last_name']
        user_profile.f_name = fullName
        user_profile.expiration_date=datetime.datetime.strftime(datetime.datetime.now() + datetime.timedelta(days=2), "%Y-%m-%d %H:%M:%S")
        user_profile.p_activation_key = "None"
        user_profile.p_expiration_date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
        if user_profile.save():
            return True
        else:
            return False
