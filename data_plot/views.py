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
def dashboard(request, al, lc):

    t_data = pd.read_csv('temp_data/dt/HB_HOUSTON.csv')
    t_data = t_data[['Date','SettlementPointPrice', 'Predicted']]
    #data  = t_data[:216712, :]
   # data1 = t_data[:, :54162]
    data = t_data.values.tolist()
    #data1 = data.values.tolist()

    #trend_data = data[['Date', 'Trend', 'Trend_macd']]
    bt_data = bt.execute_backtesting(lc)
    bt_data=bt_data.values.tolist()

    
    bd_data = (np.random.randint(1, 2, 1000) * -1).reshape(-1,1)
    bd_data =bd_data.tolist()
    print(bd_data)
    context = {
        'data' : data, #train data
        #'data1': data1, #test data
        'bt_data':bt_data, # backtesting data
        'bd_data':bd_data,
        #'trend_data': trend_data.values.tolist()
    }
    return render(
        request,
        'data_plot/index.html',
        context
    )

