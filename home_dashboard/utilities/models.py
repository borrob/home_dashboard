"""
Specify the data models for the utilities app.
"""
from django.db import models


# Create your models here.
class Meter(models.Model):
    """
    The meter model specifies the parameters of the meter.
    """
    meter_name = models.CharField(max_length=30, unique=True)
    meter_unit = models.CharField(max_length=10)

    def __str__(self):
        return 'Meter ' + self.meter_name + ' with unit: ' + self.meter_unit

    def __repr__(self):
        return "Meter(meter_name='{m}', meter_unit='{u}')".format(m=self.meter_name,
                                                                  u=self.meter_unit)

class Reading(models.Model):
    """
    The reading model specifies the meter readings.
    """
    date = models.DateField()
    reading = models.DecimalField(max_digits=10, decimal_places=2)
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE)
    remark = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('date', 'meter')

    def __str__(self):
        return 'Reading: {d} {m} - {r} {u}'.format(r=self.reading,
                                                   u=self.meter.meter_unit,
                                                   d=self.date,
                                                   m=self.meter.meter_name)

    def __repr__(self):
        return "Reading(date='{d}', reading='{r}', meter='{m}', remark='{rm}')" \
                    .format(d=self.date,
                            r=self.reading,
                            m=self.meter.id,
                            rm=self.remark)

class Usage(models.Model):
    """
    The usage tells the meter readings per month.
    """
    month = models.IntegerField()
    year = models.IntegerField()
    meter = models.ForeignKey(Meter, on_delete=models.CASCADE)
    usage = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('year', 'month', 'meter')


    def __str__(self):
        return "Usage: {y}-{m}: {u} {unit} for {meter}".format(y=self.year,
                                                               m=self.month,
                                                               u=self.usage,
                                                               unit=self.meter.meter_unit,
                                                               meter=self.meter.meter_name)

    def __repr__(self):
        return "Usage(month={m}, year={y}, meter={meter}, usage={u})".format(m=self.month,
                                                                             y=self.year,
                                                                             meter=self.meter.id,
                                                                             u=self.usage)
