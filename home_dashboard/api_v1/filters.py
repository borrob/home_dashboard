"""
Prepares the filters for the REST backend.
"""

from django_filters import rest_framework as filters

from utilities.models import Meter, Reading, Usage

class MeterFilter(filters.FilterSet):
    """
    Provides filter functionality for the meter model.
    """
    class Meta:
        model = Meter
        fields = ['meter_name', 'meter_unit']


class ReadingFilter(filters.FilterSet):
    """
    Provides filter functionality for the reading model.
    """
    class Meta:
        model = Reading
        fields = ['meter', 'date', 'reading']


class UsageFilter(filters.FilterSet):
    """
    Provides filter functionality for the Usage model.
    """
    class Meta:
        model = Usage
        fields = ['month', 'year', 'meter']
