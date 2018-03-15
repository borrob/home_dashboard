"""
Defining the dashboard views: URL links and their responses.
"""
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
    return render(request, 'dashboard/profile.html', {})
