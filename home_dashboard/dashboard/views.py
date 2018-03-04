from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
def index(request):
    """
    Generate the dashboard index-file.
    """
    return HttpResponse("Placeholder for the dashboard index.")
