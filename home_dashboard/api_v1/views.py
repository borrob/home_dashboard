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


@api_view(['GET', 'POST'])
def reading_list(request): #pylint: disable=inconsistent-return-statements
    """
    Shows the entire set of readings.

    get: shows the entire set of readings
    post: create new reading and update the usage calculation
    """
    if request.method == 'GET':
        readinglist = Reading.objects.all()
        serializer = ReadingSerializer(readinglist, many=True, context={'request': request})
        return Response(serializer.data)

    if request.method == 'POST':
        if not request.user.has_perm('utilities.add_reading'):
            raise PermissionDenied(detail='You do not have the permission to add a new reading.')
        serializer = ReadingSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            update_usage_after_new_reading(Reading.objects.get(pk=serializer.data.get('id')))
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
def reading_detail(request, id): #pylint: disable=inconsistent-return-statements, redefined-builtin, invalid-name
    """
    Show the details of a specific reading

    get: show the detail information
    put: update the data

    :param request: the http request
    :param int reading_id: the id of the request reading
    :return: http-response with data, or error
    """
    if not id:
        raise ParseError('ID of reading not supplied')

    try:
        reading = Reading.objects.get(pk=id)
    except Reading.DoesNotExist:
        raise NotFound('No reading with this ID.')

    if request.method == 'GET':
        serializer = ReadingSerializer(reading, context={'request': request})
        return Response(serializer.data)

    if request.method == 'PUT':
        if not request.user.has_perm('utilities.change_reading'):
            raise PermissionDenied(detail='You do not have the permission to change a reading.')

        reading.date = request.data.get('date', reading.date)
        try:
            meter = Meter.objects.get(pk=request.data.get('meter', reading.meter.id))
        except Meter.DoesNotExist:
            raise NotFound('No such meter id')
        reading.meter = meter
        reading.reading = request.data.get('reading', reading.reading)
        reading.remark = request.data.get('remark', reading.remark)
        reading.save()
        serializer = ReadingSerializer(reading, context={'request': request})
        update_usage_after_new_reading(reading)
        return Response(serializer.data, status=status.HTTP_200_OK)
