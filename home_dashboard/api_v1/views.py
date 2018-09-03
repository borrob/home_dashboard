"""
Provides the views for the REST interface.
"""
from calendar import monthrange

from rest_framework import permissions, viewsets
from django_filters import rest_framework as filters
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

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
    filter_backends = (filters.DjangoFilterBackend,)
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


@login_required
def monthly_usage(request):
    year = int(request.GET.get('year', -1))
    meter = int(request.GET.get('meter', -1))
    usages = Usage.objects.filter(meter__id=meter).filter(year=year)
    data = []
    for i in range(1, 12 + 1):
        try:
            usage = usages.get(month=i)
        except Usage.DoesNotExist:
            data.append(None)
        else:
            days_in_month = monthrange(year, i)[1]
            data.append(usage.usage/days_in_month)
    output = {'label': year, 'data': data}
    return JsonResponse(output)
