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
def dashboard(request, al, lc):
    
    location= 'algorithm/models/'+ al +'/'+ lc +'/predicted.csv'
    t_data = pd.read_csv(location)
    folders = list(glob('algorithm/models/*'))
    print(folders)
    t_data = t_data[['Date','SettlementPointPrice', 'Predicted', 'Direction', 'Indicator']]
    
    direction = t_data[['Date','Direction']]
    direction = direction.values.tolist()
    print(direction);
    training = t_data[t_data['Indicator'] == 1]
    test = t_data[t_data['Indicator'] == 0]
    training = training.values.tolist()
    test = test.values.tolist()

    #trend_data = data[['Date', 'Trend', 'Trend_macd']]
    #bt_data = bt.execute_backtesting(lc)
    #bt_data=bt_data.values.tolist()
    context = {
       # 'data' : data,
        'training':training,
        'test':test,
        'direction': direction
    }
    return render(
        request,
        'data_plot/index.html',
        context
    )

