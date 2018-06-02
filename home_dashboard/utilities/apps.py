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
        from django.db.models.signals import post_save
        from .signals import reading_saved
        from .models import Reading
        post_save.connect(reading_saved, sender=Reading)
