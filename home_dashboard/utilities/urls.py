from django.urls import path

from . import views

app_name = 'utilities'

urlpatterns = [
    path('meterlist', views.ListMeters.as_view(), name='meter_list'),
    path('addmeter', views.add_meter, name='add_meter'),
]