"""
Supplies the signals for the utility app.
"""
from .logic import update_usage_after_new_reading
from .models import Reading, Usage


def reading_saved(sender, instance, **kwargs): # pylint: disable=unused-argument
    """
    Calculate the new usage when a reading is saved.
    """
    if sender == Reading:
        update_usage_after_new_reading(Reading.objects.get(pk=instance.pk))

def reading_deleted(sender, instance, **kwargs): # pylint: disable=unused-argument
    """
    Calculate the new usage after a reading was deleted.
    """
    if sender == Reading:
        update_usage_after_new_reading(instance)

def reading_changed_meter(sender, instance, **kwargs): # pylint: disable=unused-argument
    """
    Checks if the meter changed
    """
    new_reading = instance
    try:
        old_reading = Reading.objects.get(pk=instance.pk)
    except Reading.DoesNotExist:
        old_reading = None

    try:
        if new_reading.meter != old_reading.meter:
            try:
                reading_before = Reading.objects.filter(meter=old_reading.meter).filter(date__lt=old_reading.date).order_by('-date')[0]
            except Reading.DoesNotExist:
                # no previous reading -> no usage -> no problem
                pass
            else:
                old_reading.delete()
                update_usage_after_new_reading(reading_before)
                reading_before.pk
    except AttributeError:
        pass