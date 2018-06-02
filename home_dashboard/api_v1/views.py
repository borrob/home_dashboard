"""
Provides the views for the REST interface.
"""
from django.db import IntegrityError
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.exceptions import NotFound, ParseError, PermissionDenied
from rest_framework.response import Response

from utilities.models import Meter, Reading, update_usage_after_new_reading
from utilities.serializers import MeterSerializer, ReadingSerializer

class MeterViewSet(viewsets.ModelViewSet):
    """
    Viewset for the meter model. Provides all the standard functions and checks permissions.
    """
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class ReadingViewSet(viewsets.ModelViewSet):
    """
    Viewset for the Reading model. Provides all the standard functions and checks permissions. When
    a new reading is added (or updated), the new usage is calculated.
    """
    queryset = Reading.objects.all()
    serializer_class = ReadingSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    #TODO: return all reading for a specific meter
