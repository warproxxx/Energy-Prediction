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
from django.db.models import Count
from . import bt
import pandas as pd
import numpy as np
from glob import glob
from django import forms
from data_plot.forms import dashboard_options

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
        form = dashboard_options()
        al ='tri_model_15_minute'
        lc = 'HB_HOUSTON'
        method = 'GET'
        return dashboard_data(request, method, al, lc, form)

    if request.method == 'POST':
        form = dashboard_options(request.POST)
        al = ''
        lc= ''
        if form.is_valid():
            #get algorithm name and location name from the form fiel
            lc  = form.cleaned_data.get("location")
            al  = form.cleaned_data.get('algorithm')
            method = 'POST'
            return dashboard_data(request, method, al, lc, form)     

def dashboard_data(request, method, al, lc, form):

    location= 'algorithm/models/'+ al +'/'+ lc +'/predicted.csv'
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
        "location":lc,
    }
    return render(
        request,
        'data_plot/backward_test.html',
        context
    )


