# Generated by Django 2.1 on 2018-09-01 10:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('f_name', models.CharField(max_length=50)),
                ('m_plans', models.CharField(max_length=10)),
                ('m_time', models.CharField(max_length=10)),
                ('activation_key', models.CharField(max_length=200)),
                ('expiration_date', models.DateTimeField()),
                ('verified', models.BooleanField(default=False)),
                ('p_activation_key', models.CharField(max_length=200)),
                ('p_expiration_date', models.DateTimeField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
