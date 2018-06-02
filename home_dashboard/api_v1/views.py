"""
Provides the views for the REST interface.
"""
from rest_framework import permissions, viewsets

from utilities.models import Meter, Reading
from utilities.serializers import MeterSerializer, ReadingSerializer

class MeterViewSet(viewsets.ModelViewSet): # pylint: disable=too-many-ancestors
    """
    Viewset for the meter model. Provides all the standard functions and checks permissions.
    """
    queryset = Meter.objects.all()
    serializer_class = MeterSerializer
    permission_classes = [permissions.DjangoModelPermissions]


class ReadingViewSet(viewsets.ModelViewSet): # pylint: disable=too-many-ancestors
    """
    Viewset for the Reading model. Provides all the standard functions and checks permissions. When
    a new reading is added (or updated), the new usage is calculated.
    """
    queryset = Reading.objects.all()
    serializer_class = ReadingSerializer
    permission_classes = [permissions.DjangoModelPermissions]
    #TODO: return all reading for a specific meter
