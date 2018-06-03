"""
Supplies the signals for the utility app.
"""
from .models import Reading, update_usage_after_new_reading


def reading_saved(sender, instance, **kwargs): # pylint: disable=unused-argument
    """
    Calculate the new usage when a reading is saved.
    """
    if sender == Reading:
        update_usage_after_new_reading(Reading.objects.get(pk=instance.pk))
