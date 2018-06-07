"""
Provide serializers for the utility models.
"""

from rest_framework import serializers
from .models import Meter, Reading, Usage

class MeterSerializer(serializers.HyperlinkedModelSerializer):
    """
    Provide a serializer for the Meter model.
    """
    url = serializers.HyperlinkedIdentityField(view_name='api_v1:meter-detail')

    class Meta:
        model = Meter
        fields = ('id', 'meter_name', 'meter_unit', 'url')

class ReadingSerializer(serializers.ModelSerializer):
    """
    Provide a serializer for the Reading model.
    """
    meter_url = serializers.SerializerMethodField()
    meter_unit = serializers.SerializerMethodField()

    def get_meter_url(self, obj):
        """
        Get the url for the connected meter.
        """
        meter = MeterSerializer(Meter.objects.get(pk=obj.meter_id),
                                context={'request': self.context.get('request')})
        return meter.data.get('url')

    def get_meter_unit(self, obj):
        """
        Get the appropiate unit of the meter.
        """
        meter = Meter.objects.get(pk=obj.meter_id)
        return meter.meter_unit

    class Meta:
        model = Reading
        fields = ('id', 'date', 'reading', 'meter', 'meter_url', 'meter_unit', 'remark')


class UsageSerializer(serializers.ModelSerializer):
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
