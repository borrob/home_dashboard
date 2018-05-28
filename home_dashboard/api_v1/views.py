"""
Provides the views for the REST interface.
"""
from django.db import IntegrityError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response

from utilities.models import Meter
from utilities.serializers import MeterSerializer

@api_view(['GET', 'POST'])
def meter_list(request): #pylint: disable=inconsistent-return-statements
    """
    Show the entire list of meters

    get: show the entire list of meter with full details
    post: create a new meter
    """
    if request.method == 'GET':
        meterlist = Meter.objects.all()
        serializer = MeterSerializer(meterlist, many=True)
        return Response(serializer.data)

    if request.method == 'POST':
        if request.user.has_perm('utilities.add_meter'):
            serializer = MeterSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise PermissionDenied(detail='You do not have permission to add a new meter',
                                   code=status.HTTP_403_FORBIDDEN)

@api_view(['GET', 'PUT'])
def meter_detail(request, meter_id): #pylint: disable=inconsistent-return-statements
    """
    Show details of a specific meter

    get: returns the details of the meter with specified id.
    put: changes the detalis of the meter with specified id and return the new details.
    """

    if not meter_id:
        return Response(None, status=status.HTTP_400_BAD_REQUEST)

    try:
        meter = Meter.objects.get(pk=meter_id)
    except Meter.DoesNotExist:
        raise NotFound('No such meter id')

    if request.method == 'GET':
        serializer = MeterSerializer(meter)
        return Response(serializer.data)

    if request.method == 'PUT':
        meter.meter_name = request.data.get('meter_name', meter.meter_name)
        meter.meter_unit = request.data.get('meter_unit', meter.meter_unit)
        try:
            meter.save()
        except IntegrityError:
            return Response('Meter name already exists', status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = MeterSerializer(meter)
            return Response(serializer.data)
