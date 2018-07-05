"""
Supplies the signals for the utility app.
"""
from .logic import update_usage_after_new_reading
from .models import Reading


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
