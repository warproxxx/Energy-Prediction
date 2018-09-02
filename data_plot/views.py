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

from .bt import perform_backtest
import os
import pandas as pd
import numpy as np
from glob import glob
from django import forms
from data_plot.forms import dashboard_options, algorithm_options, userLoginForm, UserRegistrationForm
import os
import json 

from .multiforms import MultiFormsView
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView

al = ''
lc = ''

def form_redir(request):
    return render(request, 'data_plot/backward_test.html')


def dashboard_data(request, method, al, lc, form, logic_form, test_type, datas):
    '''
    Parameters:
    ___________
    request (request):
    The web request
    
    method (string):
    POST or GET

    al (string):
    The name of algorithm

    lc (string):
    The name of city

    form (form):
    option form data

    logic_form (form):


    test_type (string):
    backtest or forwardtest

    datas: (dictionary)
    POST data belonging to the form
    '''

    if ('starting_cash' not in datas):
        datas['starting_cash'] = 10000
        datas['comission_percentage'] = 0.01
        datas['strategy_type'] = "s1"
        datas['test_type'] = test_type

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

    #chart details and guide
    strategy_explanation =''
    with open("algorithm/explanations/backtest_algorithm/"+datas["strategy_type"]+".json") as json_file:
        strategy_explanation = json.load(json_file)
    
    bt_chart_explanation =''    #backtest chart explanation
    with open("algorithm/explanations/backtest_chart.json") as json_file:
        bt_chart_explanation = json.load(json_file)
    
    bd_chart_explanation =''    #bidirectional chart explanation
    with open("algorithm/explanations/bidirectional_accuracy_chart.json") as json_file:
        bd_chart_explanation = json.load(json_file)

    tt_chart_explanation =''    #training and test set chart explanation
    with open("algorithm/explanations/training_test_set_chart.json") as json_file:
        tt_chart_explanation = json.load(json_file)

    portfolio_chart_explanation =''    #portfolio movement chart explanation
    with open("algorithm/explanations/portfolio_movement_chart.json") as json_file:
        portfolio_chart_explanation = json.load(json_file)

    model_performance_explanation =''    #model performance explanation
    with open("algorithm/explanations/model_performance.json") as json_file:
        model_performance_explanation = json.load(json_file)

    risk_explanation =''    #risk metrics explanation
    with open("algorithm/explanations/risk_metrics.json") as json_file:
        risk_explanation = json.load(json_file)

    #End chart details and guide


    portfolioValue, trade_data, strategy_metrics, benchmark_metrics, strategyMovementDetails, benchmarkMovementDetails = perform_backtest(lc, al, test_type, datas['starting_cash'], datas['comission_percentage'], datas['strategy_type'])
        
    bt_metrics = strategy_metrics #remove this one later. It is useless
    portfolioValue = portfolioValue.values.tolist()

    buy_data =trade_data[['Date','Buy']].dropna().reset_index(drop=True)
    buy_data = buy_data.values.tolist()
    
    sell_data =trade_data[['Date','Sell']].dropna().reset_index(drop=True)
    sell_data = sell_data.values.tolist()

    t_data = pd.read_csv(location) 

    trade_data = t_data[['Date','SettlementPointPrice']]
    trade_data = trade_data.values.tolist() 

    t_data = t_data[['Date','SettlementPointPrice', 'Predicted', 'Direction', 'Indicator']]
    
    direction = t_data[['Date','Direction']]
    actual = t_data['SettlementPointPrice'].shift(-1) > t_data['SettlementPointPrice']
    direction['Direction'] = ((1 - np.abs(t_data['Direction'] - actual)).replace(0, -1)).cumsum()
    direction = direction.values.tolist()

    training = t_data[t_data['Indicator'] == 1]
    training = training.values.tolist()

    test = t_data[t_data['Indicator'] == 0]
    test = test.values.tolist()

    s_pMovementDetails = benchmarkMovementDetails.values.tolist()
    strategyMovementDetails = strategyMovementDetails.values.tolist()

    


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
        "strategyMovementDetails":strategyMovementDetails,
        "s_pMovementDetails":s_pMovementDetails,
        "strategy_explanation":strategy_explanation,
        "bt_chart_explanation":bt_chart_explanation,
        "bd_chart_explanation":bd_chart_explanation,
        "tt_chart_explanation":tt_chart_explanation,
        "portfolio_chart_explanation":portfolio_chart_explanation,
        "model_performance_explanation":model_performance_explanation,
        "risk_explanation":risk_explanation,
        
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
                datas['comission_percentage']  = 0.1
                datas['strategy_type']  = logic_form.cleaned_data.get("strategy_type")
                datas['test_type']  = logic_form.cleaned_data.get("test_type")

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
                datas['comission_percentage']  = 0.1
                datas['strategy_type']  = logic_form.cleaned_data.get("strategy_type")
                datas['test_type']  = logic_form.cleaned_data.get("test_type")

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

def login_user(request):
    template_name = 'data_plot/login.html'

    if request.method == 'GET':
        if request.user.is_authenticated == True:
            return HttpResponseRedirect("/dashboard/backtest/")
        else:
            form = userLoginForm()
            return render(request, template_name, {"form":form})
            

    if request.method == 'POST':
        if request.user.is_authenticated == True:
            return HttpResponseRedirect("/dashboard/backtest/")
        else:
            form = userLoginForm(request.POST)
            if form.is_valid():
                uname  = form.cleaned_data.get("username")
                pword  = form.cleaned_data.get('password')
                user = authenticate(username=uname, password=pword)      
                login(request, user)
                if login:
                    return HttpResponseRedirect("/dashboard/backtest")
                else:   
                    return redirect("/login/")
        return render(request, template_name, {"form":form})

def user_logout(request):
    if not request.user.is_authenticated:
        return redirect("/dashboard/login/")
    else:
        logout(request)
        return redirect("/dashboard/login/")


class register_user(TemplateView):
    template_name = 'data_plot/adduser.html'
    def get(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            #data=request.GET
            membership = '6m'
            membership_plan = 'platinium'
            plan_check = False
            time_check = False
            if membership == '1m' or membership == '3m' or membership == '6m' or membership == '7d':
                plan_check = True
            else:
                plan_check = False
            if membership_plan=='premium' or membership_plan == 'platinium' or membership_plan == 'trial':
                time_check = True
            else:
                time_check = False

            if plan_check == True and time_check == True:
                form = UserRegistrationForm()
                return render(self.request, self.template_name, {"form":form, 'plan':membership_plan, 'time':membership})
            else:
                return HttpResponseRedirect("/Error-404/")
        else:
            return HttpResponseRedirect("/dashboard/backtest/")

    def post(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            template_name = 'data_plot/adduser.html'
            #next = request.GET.get('next')
            membership = '6m'
            membership_plan = 'platinium'
            membership_title=''
            plan_check = False
            time_check = False
            if membership == '1m' or membership == '3m' or membership == '6m' or membership == '7d':
                plan_check = True
            else:
                plan_check = False
            if membership_plan=='premium' or membership_plan == 'platinium' or membership_plan == 'trial':
                time_check = True
            else:
                time_check = False
            
            if plan_check == True and time_check == True:
                form = UserRegistrationForm(request.POST)
                if form.is_valid():
                    datas={}
                    datas['username']=form.cleaned_data['username']
                    datas['email']=form.cleaned_data['email']
                    datas['password1']=form.cleaned_data['password1']
                    datas['first_name']=form.cleaned_data['first_name']
                    datas['last_name']=form.cleaned_data['last_name']
                    datas['m_plans']=plan
                    datas['m_time'] = time
                    datas['activation_key']= generate_activation_key(datas['username'])
                    datas['link']="http://127.0.0.1:8000/user_registration/activate_account/"+datas['activation_key']
                    datas['subject']='Quantorithm: Email Confirmation Token'
                    saveData = form.save(datas)
                    if saveData:
                        return HttpResponseRedirect("dashboard/backtest")
                else:     
                    args =  {"form":form}
                    return render(request, template_name, args)
                
            else:
                return HttpResponseRedirect("/Error-404/")
        else:
            return HttpResponseRedirect("/dashboard/backtest/")