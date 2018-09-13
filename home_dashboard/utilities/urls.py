"""
Maps the utilities URLs to the python functions.
"""
from django.urls import path

from . import views

app_name = 'utilities'

urlpatterns = [
    path('meterlist', views.show_meters, name='meter_list'),
    path('meter/', views.meter, name='meter'),
    path('meter/<int:meter_id>/', views.meter, name='meter'),
    path('deletemeter', views.delete_meter, name='delete_meter'),
    path('readinglist', views.list_readings, name='reading_list'),
    path('reading', views.reading, name='reading'),
    path('reading/<int:reading_id>/', views.reading, name='reading'),
    path('deletereading', views.delete_reading, name='delete_reading'),
    path('usagelist', views.list_usages, name='usage_list'),
    path('graphs', views.graphs, name='graphs')
]
