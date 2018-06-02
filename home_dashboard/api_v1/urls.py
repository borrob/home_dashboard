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
router.register(r'reading', views.ReadingViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]

