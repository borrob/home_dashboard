"""
Specify the data models for the utilities app.
"""
from django.db import models

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
