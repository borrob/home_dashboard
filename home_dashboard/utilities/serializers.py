"""
Provide serializers for the utility models.
"""

from rest_framework import serializers
from .models import Meter, Reading

class MeterSerializer(serializers.ModelSerializer):
    """
    Provide a serializer for the Meter model.
    """
    class Meta:
        model = Meter
        fields = ('id', 'meter_name', 'meter_unit')

class ReadingSerializer(serializers.ModelSerializer):
    """
    Provide a serializer for the Reading model.
    """
    class Meta:
        model = Reading
        fields = ('id', 'date', 'reading', 'meter', 'remark')
