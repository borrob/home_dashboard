"""
Provide serializers for the utility models.
"""

from rest_framework import serializers
from .models import Meter

class MeterSerializer(serializers.ModelSerializer):
    """
    Provide a serializer for the Meter model.
    """
    class Meta:
        model = Meter
        fields = ('id', 'meter_name', 'meter_unit')
