from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.shortcuts import render, redirect, reverse

from .models import Meter

# Create your views here.
class ListMeters(LoginRequiredMixin, generic.ListView):
    model = Meter
    template = 'utilities/meter_list.html'

@permission_required('utilities.add_meter')
def add_meter(request):
    """
    Add a meter.
    """
    try:
        meterName = request.POST.get('meter_name')
        meterUnit = request.POST.get('unit_name')
    except KeyError:
        messages.add_message(request, messages.ERROR, 'Missing key element to add a new meter.', 'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    if(meterName == None or meterUnit == None):
        messages.add_message(request, messages.ERROR, 'Missing key element to add a new meter.', 'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    try:
        Meter.objects.get(meter_name=meterName)
    except Meter.DoesNotExist:
        #meter doesn't exist -> OK!
        pass
    else:
        messages.add_message(request, messages.ERROR, 'Meter already exists. Cannot add a double entry.', 'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    newMeter = Meter.objects.create(meter_name=meterName, meter_unit=meterUnit)
    newMeter.save()
    messages.add_message(request, messages.INFO, 'Meter {0} is added.'.format(newMeter.meter_name), 'alert-success')
    return redirect(reverse('utilities:meter_list'))
