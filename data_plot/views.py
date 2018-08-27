from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import(
    authenticate,
    login,
    logout,
)
from django.db.models import Count
from django.shortcuts import render, get_object_or_404

from . import bt
import os
import pandas as pd
import numpy as np
from glob import glob
from django import forms
from data_plot.forms import dashboard_options, algorithm_options

import json 

from .multiforms import MultiFormsView
from django.urls import reverse, reverse_lazy

al = ''
lc = ''

def form_redir(request):
    return render(request, 'data_plot/backward_test.html')


def dashboard_data(request, method, al, lc, form, logic_form, test_type):
    location= 'algorithm/models/'+ al +'/'+ lc +'/'+test_type+'/predicted.csv'
    about = ''
    metrics = ''
    with open('algorithm/models/'+ al + "/about.json") as json_file:
        about = json.load(json_file)
    
    with open('algorithm/models/'+ al +'/'+ lc +'/'+test_type+'/metrics.json') as aa:
        metrics = json.load(aa)
    
    metrics = json.loads(metrics)
    t_data = pd.read_csv(location)

    t_data = t_data[['Date','SettlementPointPrice', 'Predicted', 'Direction', 'Indicator']]
    backtest_data = t_data[['Date','SettlementPointPrice', 'Predicted']][:100]

    direction = t_data[['Date','Direction']]
    direction = direction.values.tolist()

    training = t_data[t_data['Indicator'] == 1]
    test = t_data[t_data['Indicator'] == 0]
    training = training.values.tolist()
    test = test.values.tolist()

    #trend_data = data[['Date', 'Trend', 'Trend_macd']]
    bt_data = bt.execute_backtesting(lc, backtest_data)
    bt_data=bt_data.values.tolist()

    context = {
        'bt_data': bt_data,
        'training':training,
        'test':test,
        'direction': direction,
        "form":form,
        "logic_form":logic_form,
        "location":lc,
        "about":about,
        "metrics":metrics,
    }
    return render(
        request,
        'data_plot/backward_test.html',
        context
    )


def dashboard_forward_test(request):
    global al, lc
    test ='forwardtest'
    if request.method == 'POST':
        option_form = dashboard_options(request.POST)
        logic_form = algorithm_options(request.POST)
        if option_form.is_valid() or logic_form.is_valid():        
            if option_form.is_valid():
                lc  = option_form.cleaned_data.get("location")
                al  = option_form.cleaned_data.get('algorithm')
                logic  = option_form.cleaned_data.get('logic_field')
                method = 'POST'
                return dashboard_data(request, method, al, lc, option_form, logic_form, test) 

            if logic_form.is_valid():
                buy  = logic_form.cleaned_data.get("buy")
                print(buy)
                method = 'buy'
                return dashboard_data(request, method, al, lc, option_form, logic_form, test) 
            

    else:
        #set default algorithm and location
        temp_models = []
        for file in glob('algorithm/models/*'):
            file = os.path.basename(file)
            temp_models.append(file)
            
        al = temp_models[0]

        temp_location = []

        for file in glob('algorithm/models/{}/*'.format(al)):
            file = os.path.basename(file)

            if ("about.json" not in file):
                temp_location.append(file)
        
        option_form = dashboard_options()
        logic_form = algorithm_options()
            
        lc = temp_location[0]
        method = 'GET'
        

        return dashboard_data(request, method, al, lc, option_form, logic_form, test)


def dashboard_backward_test(request):
    global al, lc
    test ='backtest'
    if request.method == 'POST':
        option_form = dashboard_options(request.POST)
        logic_form = algorithm_options(request.POST)
        if option_form.is_valid() or logic_form.is_valid():        
            if option_form.is_valid():
                lc  = option_form.cleaned_data.get("location")
                al  = option_form.cleaned_data.get('algorithm')
                logic  = option_form.cleaned_data.get('logic_field')
                method = 'POST'
                return dashboard_data(request, method, al, lc, option_form, logic_form, test) 

            if logic_form.is_valid():
                buy  = logic_form.cleaned_data.get("buy")
                print(buy)
                method = 'buy'
                return dashboard_data(request, method, al, lc, option_form, logic_form, test) 
            

    else:
        #set default algorithm and location
        temp_models = []
        for file in glob('algorithm/models/*'):
            file = os.path.basename(file)
            temp_models.append(file)
            
        al = temp_models[0]

        temp_location = []

        for file in glob('algorithm/models/{}/*'.format(al)):
            file = os.path.basename(file)

            if ("about.json" not in file):
                temp_location.append(file)

        
        option_form = dashboard_options()
        logic_form = algorithm_options()
            
        lc = temp_location[0]
        method = 'GET'
        return dashboard_data(request, method, al, lc, option_form, logic_form, test)

        

class MultipleFormsDemoView(MultiFormsView):
    template_name = 'data_plot/backward_test.html'
    form_classes = {'option': dashboard_options,
                    'logic': algorithm_options,
                    }

    success_urls = {
        'option_form': reverse_lazy('form-redirect'),
        'logic_form': reverse_lazy('form-redirect'),
    }

    def option_form_valid(self, form):
        lc  = form.cleaned_data.get("location")
        print(lc)
        return HttpResponseRedirect(self.get_success_url(form_name))
    
    def logic_form_valid(self, form):
        buy= form.cleaned_data.get('buy')
        print(buy)
        return HttpResponseRedirect(self.get_success_url(form_name))
