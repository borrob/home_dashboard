from django.contrib import admin

from .models import Meter, Reading, Usage

admin.site.register(Meter)
admin.site.register(Reading)
admin.site.register(Usage)
