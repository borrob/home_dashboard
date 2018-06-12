"""
Provides the views for the REST interface.
"""
from rest_framework import permissions, viewsets
from django_filters import rest_framework as filters
from rest_framework.filters import OrderingFilter

from utilities.models import Meter, Reading, Usage
from utilities.serializers import MeterSerializer, ReadingSerializer, UsageSerializer

from .filters import MeterFilter, ReadingFilter, UsageFilter

class MeterViewSet(viewsets.ModelViewSet): # pylint: disable=too-many-ancestors
    """
    Viewset for the meter model. Provides all the standard functions and checks permissions.
    """
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = (filters.DjangoFilterBackend, OrderingFilter)
    filter_class = MeterFilter


class ReadingViewSet(viewsets.ModelViewSet): # pylint: disable=too-many-ancestors
    """
    Viewset for the Reading model. Provides all the standard functions and checks permissions. When
    a new reading is added (or updated), the new usage is calculated.
    """
    queryset = Reading.objects.all()
    serializer_class = ReadingSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = ReadingFilter


class UsageViewSet(viewsets.ReadOnlyModelViewSet): # pylint: disable=too-many-ancestors
    """
    Viewset for the usage model. Only readonly actions are provided.
    """
    queryset = Usage.objects.all()
    serializer_class = UsageSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = UsageFilter
