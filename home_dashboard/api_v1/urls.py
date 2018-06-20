"""
Maps the utilities URLs to the python functions.
"""
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'api_v1'

router = DefaultRouter() # pylint: disable=invalid-name
router.register(r'meter', views.MeterViewSet)
router.register(r'reading', views.ReadingViewSet)
router.register(r'usage', views.UsageViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
