from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.shortcuts import render

from .models import Meter

# Create your views here.
class ListMeters(generic.ListView):
    model = Meter
    template = 'utilities/meter_list.html'
