from django.urls import path, re_path
from . import views
from django.conf.urls import url, include
from django.contrib.auth.views import login

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]