from django.urls import path

from . import views

app_name = 'utilities'

urlpatterns = [
    path('meterlist', views.ListMeters.as_view(), name='meter_list'),
    path('addmeter', views.add_meter, name='add_meter'),
    path('deletemeter', views.delete_meter, name='delete_meter'),
    path('editmeter', views.edit_meter, name='edit_meter'),
    path('readinglist', views.list_readings, name='reading_list'),
    path('addreading', views.add_reading, name='add_reading'),
    path('deletereading', views.delete_reading, name='delete_reading'),
    path('editreading', views.edit_reading, name='edit_reading')
]
