"""
Specify the data models for the utilities app.
"""
from django.db import models

from .exceptions import MeterError, ReadingError

# Create your models here.
class Meter(models.Model):
    """
    The meer model specifies the parameters of the meter.
    """
    meter_name = models.CharField(max_length=30)
    meter_unit = models.CharField(max_length=10)

    def __str__(self):
        return 'Meter ' + self.meter_name + ' with unit: ' + self.meter_unit

class Reading(models.Model):
    """
    The reading model specifies the meter readings.
    """
    date = models.DateField()
    reading = models.DecimalField(max_digits=10, decimal_places=2)
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE)
    remark = models.CharField(max_length=255)

    def __str__(self):
        return 'Reading: {d} {m} - {r} {u}'.format(r=self.reading,
                                                   u=self.meter.meter_unit,
                                                   d=self.date,
                                                   m=self.meter.meter_name)

def calculate_reading_on_date(the_date, reading_1, reading_2):
    """
    Calculate the useage on the_date based on the the input readings.

    Raises errors when something is not good.
    """
    if reading_1.meter != reading_2.meter:
        raise MeterError('Meters are not equal, cannot calculate usegage.')
    if reading_1.date == reading_2.date:
        raise ReadingError('Readings are of the same reader on the same date.')
    if reading_1.date > reading_2.date:
        # making sure 1 is before 2
        reading_1, reading_2 = reading_2, reading_1
    if the_date < reading_1.date or the_date > reading_2.date:
        raise ValueError('The specified date is not between the dates of the readings.')

    days_between_readings = (reading_2.date - reading_1.date).days
    days_since_reading_1 = (the_date - reading_1.date).days
    usage_between_reading = reading_2.reading - reading_1.reading
    reading_on_date = reading_1.reading \
                      + usage_between_reading \
                      * days_since_reading_1/days_between_readings
    return reading_on_date
