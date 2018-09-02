from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class profile(models.Model):
     user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
     f_name = models.CharField(max_length = 50)
     m_plans = models.CharField(max_length = 10)
     m_time = models.CharField(max_length = 10)
     activation_key = models.CharField(max_length=200)
     expiration_date = models.DateTimeField()
     verified = models.BooleanField(default=False)
     p_activation_key = models.CharField(max_length=200)
     p_expiration_date = models.DateTimeField()