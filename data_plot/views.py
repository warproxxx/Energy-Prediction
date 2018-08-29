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
import os
import json 

from .multiforms import MultiFormsView
from django.urls import reverse, reverse_lazy

al = ''
lc = ''

def form_redir(request):
    return render(request, 'data_plot/backward_test.html')


def dashboard_data(request, method, al, lc, form, logic_form, test_type, datas):
    location= 'algorithm/models/'+ al +'/'+ lc +'/'+test_type+'/predicted.csv'
    about = ''
    f_metrics = ''
    b_metrics =''
    with open('algorithm/models/'+ al + "/about.json") as json_file:
        about = json.load(json_file)
    
    with open('algorithm/models/'+ al +'/'+ lc +'/'+'backtest'+'/metrics.json') as aa:
        b_metrics = json.load(aa)
    backward_metrics = json.loads(b_metrics)

    with open('algorithm/models/'+ al +'/'+ lc +'/'+'forwardtest'+'/metrics.json') as aa:
        f_metrics = json.load(aa)
    forward_metrics = json.loads(f_metrics)

    with open('algorithm/csvs/backtestMetrics.json') as aa:
        bt_metrics = json.load(aa)
    bt_metrics = json.loads(bt_metrics)

    with open('algorithm/csvs/s&pMetrics.json') as aa:
        benchmark_metrics = json.load(aa)
    benchmark_metrics = json.loads(benchmark_metrics)

    with open('algorithm/csvs/strategyMetrics.json') as aa:
        strategy_metrics = json.load(aa)
    strategy_metrics = json.loads(strategy_metrics)

    t_data = pd.read_csv(location)

    operations = pd.read_csv('algorithm/csvs/operations.csv')
    operations = operations.values.tolist()

    portfolioValue = pd.read_csv('algorithm/csvs/PortfolioValue.csv')
    portfolioValue = portfolioValue.values.tolist()


    trade_data = pd.read_csv('algorithm/csvs/trading_data.csv')
    buy_data =trade_data[['Date','Buy']].dropna().reset_index(drop=True)
    print(buy_data)
    buy_data = buy_data.values.tolist()
    
    sell_data =trade_data[['Date','Sell']].dropna().reset_index(drop=True)
    sell_data = sell_data.values.tolist()

    trade_data = t_data[['Date','SettlementPointPrice']]
    trade_data = trade_data.values.tolist()


    t_data = t_data[['Date','SettlementPointPrice', 'Predicted', 'Direction', 'Indicator']]
    
    direction = t_data[['Date','Direction']]
    actual = t_data['SettlementPointPrice'].shift(-1) > t_data['SettlementPointPrice']
    direction['Direction'] = ((1 - np.abs(t_data['Direction'] - actual)).replace(0, -1)).cumsum()
    direction = direction.values.tolist()

    training = t_data[t_data['Indicator'] == 1]
    test = t_data[t_data['Indicator'] == 0]
    training = training.values.tolist()
    test = test.values.tolist()

    #trend_data = data[['Date', 'Trend', 'Trend_macd']]
    #bt_data = bt.execute_backtesting(lc, backtest_data, datas)
    #bt_data=bt_data.values.tolist()
    
    context = {
        'trade_data':trade_data,
        'test':test,
        'direction': direction,
        "form":form,
        "logic_form":logic_form,
        "location":lc,
        "about":about,
        "backward_metrics":backward_metrics,
        "forward_metrics":forward_metrics,
        "test_type":test_type,
        "trade_data":trade_data,
        "sell_data":sell_data,
        "buy_data":buy_data,
        "portfolioValue":portfolioValue,
        "bt_metrics":bt_metrics,
        "benchmark_metrics":benchmark_metrics,
        "strategy_metrics":strategy_metrics,
    }

    template_name = ''
    if test_type == 'backtest':
        template_name = 'data_plot/backward_test.html'
        context['training']=training
    elif test_type == 'forwardtest':
        template_name = 'data_plot/forward_test.html'

    return render(
        request,
        template_name,
        context
    )


def dashboard_forward_test(request):
    global al, lc
    test ='forwardtest'
    
    if request.method == 'POST':
        method = 'POST'
        option_form = dashboard_options(request.POST)
        logic_form = algorithm_options(request.POST)
        if option_form.is_valid() or logic_form.is_valid():        
            if option_form.is_valid():
                datas= {}
                lc  = option_form.cleaned_data.get("location")
                al  = option_form.cleaned_data.get('algorithm')
                logic  = option_form.cleaned_data.get('logic_field')
                method = 'POST'
                return dashboard_data(request, method, al, lc, option_form, logic_form, test, datas) 

            if logic_form.is_valid():
                datas={}
                datas['starting_cash']  = logic_form.cleaned_data.get("starting_cash")
                datas['comission_percentage']  = logic_form.cleaned_data.get("comission_percentage")
                datas['strategy_type']  = logic_form.cleaned_data.get("strategy_type")

                return dashboard_data(request, method, al, lc, option_form, logic_form, test, datas) 
            

    else:
        #set default algorithm and location
        temp_models = []
        datas ={}
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
        

        return dashboard_data(request, method, al, lc, option_form, logic_form, test, datas)


def dashboard_backward_test(request):
    global al, lc
    test ='backtest'
    if request.method == 'POST':
        method = 'POST'
        option_form = dashboard_options(request.POST)
        logic_form = algorithm_options(request.POST)
        if option_form.is_valid() or logic_form.is_valid():        
            if option_form.is_valid():
                datas= {}
                lc  = option_form.cleaned_data.get("location")
                al  = option_form.cleaned_data.get('algorithm')
                logic  = option_form.cleaned_data.get('logic_field')
                return dashboard_data(request, method, al, lc, option_form, logic_form, test, datas) 

            if logic_form.is_valid():
                datas={}
                datas['starting_cash']  = logic_form.cleaned_data.get("starting_cash")
                datas['comission_percentage']  = logic_form.cleaned_data.get("comission_percentage")
                datas['strategy_type']  = logic_form.cleaned_data.get("strategy_type")
                datas['test_type']  = logic_form.cleaned_data.get("strategy_type")

                return dashboard_data(request, method, al, lc, option_form, logic_form, test, datas) 
            

    else:
        #set default algorithm and location
        temp_models = []
        datas ={}
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
        return dashboard_data(request, method, al, lc, option_form, logic_form, test, datas)

        

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