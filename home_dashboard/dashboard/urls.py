"""
Maps the dashboard URLs to the python functions.
"""
from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    path('profile', views.profile, name='profile')
]
