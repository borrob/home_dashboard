from django.db import models

# Create your models here.
class Meter(models.Model):
    meter_name = models.CharField(max_length=30)
    meter_unit = models.CharField(max_length=10)
    
    def __str__(self):
        return('Meter ' + self.meter_name + ' with unit: ' + self.meter_unit)
