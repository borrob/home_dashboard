"""
Maps the utilities URLs to the python functions.
"""
from django.conf.urls import url, include
from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework.urlpatterns import format_suffix_patterns

from . import views

app_name = 'api_v1'

router = DefaultRouter()
router.register(r'meter', views.MeterViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
     path('readings', views.reading_list, name='reading_list'),
     path('reading/<int:id>', views.reading_detail, name='reading_details')
]

