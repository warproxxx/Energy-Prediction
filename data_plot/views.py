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
import pandas as pd

def dashboard(request):
    data = pd.read_csv('algorithm/data/HB_HOUSTON.csv')
    data = data[['price', 'predicted_price']]
    #trend_data = data[['Date', 'Trend', 'Trend_macd']]
    context = {
        'data' : data.values.tolist(),
        #'trend_data': trend_data.values.tolist()
    }
    return render(
        request,
        'data_plot/dashboard.html',
        context
    )
