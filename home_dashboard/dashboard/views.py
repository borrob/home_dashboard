"""
Defining the dashboard views: URL links and their responses.
"""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

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
    version = settings.VERSION
    return render(request, 'dashboard/profile.html', {'version': version})
