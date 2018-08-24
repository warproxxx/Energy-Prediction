from django.urls import path, re_path
from . import views
from django.conf.urls import url, include
from django.contrib.auth import login

urlpatterns = [
    url(r'(?P<al>.+)/(?P<lc>.+)/$', views.dashboard, name='dashboard'),
]
