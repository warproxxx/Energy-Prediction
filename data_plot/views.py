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
import pandas as pd
import numpy as np
from glob import glob
from django import forms
from data_plot.forms import dashboard_options, algorithm_options
import json 
def dashboard_forward_test(request, al, lc):
    
    location= 'algorithm/models/'+ al +'/'+ lc +'/predicted.csv'
    t_data = pd.read_csv(location)
    folders = list(glob('algorithm/models/*'))
    print(folders)

    t_data = t_data[['Date','SettlementPointPrice', 'Predicted', 'Direction', 'Indicator']]
    backtest_data = t_data[['Date','SettlementPointPrice', 'Predicted']][:1000]

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
        'direction': direction
    }
    return render(
        request,
        'data_plot/backward_test.html',
        context
    )

def dashboard_backward_test(request):
    if request.method == 'GET':
        #set default algorithm and location
        temp_models = []
        for file in glob('algorithm/models/*'):
            file = file.replace('algorithm/models\\', '')
            temp_models.append(file)
            
        al = temp_models[0]

        temp_location = []
        for file in glob('algorithm/models/{}/*'.format(al)):
            file = file.replace('algorithm/models/'+al, '')
            file = file.replace("\\", '/')
            file = file.replace("/", '')
            if ("about.json" not in file):
                temp_location.append(file)

        
        form = dashboard_options()
        logic_form = algorithm_options()
        lc = temp_location[0]
        method = 'GET'
        test ='backtest'
        return dashboard_data(request, method, al, lc, form, logic_form, test)

    if request.method == 'POST':
        form = dashboard_options(request.POST)
        al = ''
        lc= ''
        test ='backtest'
        
        if form.is_valid():
            #get algorithm name and location name from the form fiel
            lc  = form.cleaned_data.get("location")
            al  = form.cleaned_data.get('algorithm')
            logic  = form.cleaned_data.get('logic_field')
            method = 'POST'
            return dashboard_data(request, method, al, lc, form, test)     

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


