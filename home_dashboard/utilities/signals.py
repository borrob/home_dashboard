from .models import Reading, update_usage_after_new_reading


def reading_saved(sender, instance, **kwargs):
    """
    Calculate the new usage when a reading is saved.
    """
    update_usage_after_new_reading(Reading.objects.get(pk=instance.pk))

