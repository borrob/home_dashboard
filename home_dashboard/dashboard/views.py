from django.shortcuts import render

# Create your views here.
def index(request):
    """
    Generate the dashboard index-file.
    """
    return render(request, 'dashboard/index.html', {})
