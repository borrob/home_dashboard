from django.db import models

# Create your models here.
class Meter(models.Model):
    meter_name = models.CharField(max_length=30)
    meter_unit = models.CharField(max_length=10)
    
    def __str__(self):
        return('Meter ' + self.meter_name + ' with unit: ' + self.meter_unit)

class Reading(models.Model):
    date = models.DateField()
    reading = models.DecimalField(max_digits=10, decimal_places=2)
    meter = models.ForeignKey('Meter', on_delete=models.CASCADE)
    remark = models.CharField(max_length=255)

    def __str__(self):
        return('Reading: {0} {1} ({2} - {3}'.format(self.reading, self.meter.meter_unit, self.date, self.meter.meter_name))
