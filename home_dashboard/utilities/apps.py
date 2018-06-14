"""
Register Utilities app.
"""
from django.apps import AppConfig

class UtilitiesConfig(AppConfig):
    """
    Register Utilities app.
    """
    name = 'utilities'

    def ready(self):
        """
        Called when loading the app and performs additional setup to register signals.

        When a reading is saved: calculate the new usage.
        """
        from django.db.models.signals import post_save, post_delete
        from .signals import reading_saved, reading_deleted
        from .models import Reading
        post_save.connect(reading_saved, sender=Reading)
        post_delete.connect(reading_deleted, sender=Reading)
