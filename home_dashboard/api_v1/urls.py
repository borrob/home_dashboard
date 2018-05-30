"""
Maps the utilities URLs to the python functions.
"""
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'api_v1'

urlpatterns = [
    path('meters', views.meter_list, name='meter_list'),
    path('meter/<int:id>', views.meter_detail, name='meter_details'),
    path('readings', views.reading_list, name='reading_list'),
    path('reading/<int:id>', views.reading_detail, name='reading_details')
]

urlpatterns = format_suffix_patterns(urlpatterns)
