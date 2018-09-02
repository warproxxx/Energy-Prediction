from django.urls import path, re_path
from . import views
from django.conf.urls import url, include
from django.contrib.auth import login

urlpatterns = [
    path('', views.dashboard_forward_test, name='default_dashboard'),
    url(r'forwardtest/$', views.dashboard_forward_test, name='dashboard'),
    url(r'backtest/$', views.dashboard_backward_test, name='dashboard'),
    url(r'login/$', views.login_user, name='login'),
    url(r'logout/$', views.user_logout, name='logout'),
    url(r'adduser/$', views.register_user.as_view(), name='logout'),
    
    
]
