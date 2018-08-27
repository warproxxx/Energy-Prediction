from django.urls import path, re_path
from . import views
from django.conf.urls import url, include
from django.contrib.auth import login

urlpatterns = [
    path('', views.dashboard_backward_test, name='default_dashboard'),
    url(r'forward/$', views.dashboard_backward_test, name='dashboard'),
    url(r'backward/$', views.dashboard_backward_test, name='dashboard'),
    
    
]
