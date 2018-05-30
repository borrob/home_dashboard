"""
Provide serializers for the utility models.
"""

from rest_framework import serializers
from .models import Meter, Reading, Usage

class MeterSerializer(serializers.HyperlinkedModelSerializer):
    """
    Provide a serializer for the Meter model.
    """
    url = serializers.HyperlinkedIdentityField(view_name='api_v1:meter_details', lookup_field='id')

    class Meta:
        model = Meter
        fields = ('id', 'meter_name', 'meter_unit', 'url')

class ReadingSerializer(serializers.ModelSerializer):
    """
    Provide a serializer for the Reading model.
    """
    meter_url = serializers.SerializerMethodField()

    def get_meter_url(self, obj):
        """
        Get the url for the connected meter.
        """
        meter = MeterSerializer(Meter.objects.get(pk=obj.meter_id),
                                context={'request': self.context.get('request')})
        return meter.data.get('url')

    class Meta:
        model = Reading
        fields = ('id', 'date', 'reading', 'meter', 'meter_url', 'remark')


class UsageSerialiser(serializers.ModelSerializer):
    """
    Provide a serializer for the Usage model.
    """
    meter_url = serializers.SerializerMethodField()

    def get_meter_url(self, obj):
        """
        Get the url for the connected meter.
        """
        meter = MeterSerializer(Meter.objects.get(pk=obj.meter_id),
                                context={'request': self.context.get('request')})
        return meter.data.get('url')

    class Meta:
        model = Usage
        fields = ('id', 'month', 'year', 'meter', 'meter_url', 'usage')
