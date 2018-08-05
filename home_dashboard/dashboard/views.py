"""
Defining the dashboard views: URL links and their responses.
"""
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

LOGGER = logging.getLogger('home_dashboard_log')


@login_required
def index(request):
    """
    Generate the dashboard index-file.
    """
    LOGGER.debug('User accesses dashboard index-page.')
    return profile(request)

@login_required
def profile(request):
    """
    Show the user profile.
    """
    LOGGER.debug('User accesses the profile page.')
    version = settings.VERSION
    return render(request, 'dashboard/profile.html', {'version': version})
