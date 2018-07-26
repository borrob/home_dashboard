"""
Defining the dashboard views: URL links and their responses.
"""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger('home_dashboard_log')

@login_required
def index(request):
    """
    Generate the dashboard index-file.
    """
    return profile(request)

@login_required
def profile(request):
    """
    Show the user profile.
    """
    logger.error('running! from the dashboard view')
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warning message')
    logger.error('error message')
    logger.critical('oopsie')
    version = settings.VERSION
    return render(request, 'dashboard/profile.html', {'version': version})
