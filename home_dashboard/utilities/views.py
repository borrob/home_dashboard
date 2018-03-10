from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.shortcuts import render, redirect, reverse

from .models import Meter, Reading

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

@permission_required('utilities.delete_meter')
def delete_meter(request):
    """
    Delete a meter
    """
    try:
        meterName = request.POST.get('meter_name')
    except KeyError:
        messages.add_message(request, messages.ERROR, 'Missing key element to delete meter.', 'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    if(meterName == None):
        messages.add_message(request, messages.ERROR, 'Missing key element to delete meter.', 'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    deleted = 0
    try:
        (deleted, deletedMeter) = Meter.objects.get(meter_name=meterName).delete()
    except Meter.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'Cannot delete already deleted meter.', 'alert-danger')
        return redirect(reverse('utilities:meter_list'))
    finally:
        if (deleted>=1):
            messages.add_message(request, messages.INFO, 'Meter {0} is deleted'.format(meterName), 'alert-success')
            return redirect(reverse('utilities:meter_list'))
        else:
            messages.add_message(request, messages.ERROR, 'Cannot delete already deleted meter.', 'alert-danger')
            return redirect(reverse('utilities:meter_list'))

@permission_required('utilities.change_meter')
def edit_meter(request):
    """
    Edit a meter.
    """
    try:
        meterName = request.POST.get('meter_name')
        newName = request.POST.get('new_name')
        meterUnit = request.POST.get('unit_name')
    except KeyError:
        messages.add_message(request, messages.ERROR, 'Missing key element to change a meter.', 'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    if(meterName == None or meterUnit == None):
        messages.add_message(request, messages.ERROR, 'Missing key element to change a meter.', 'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    try:
        theMeter = Meter.objects.get(meter_name=meterName)
    except Meter.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'Cannot change a meter that doesn\'t exist yet.', 'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    try:
        m = Meter.objects.get(meter_name=newName)
    except Meter.DoesNotExist:
        #new name isn't taken -> OK!
        pass
    else:
        if(m.pk != theMeter.pk):
            #just changing the unit name
            messages.add_message(request, messages.ERROR, 'Name is already taken', 'alert-danger')
            return redirect(reverse('utilities:meter_list'))

    theMeter.meter_name = newName
    theMeter.unit_name = meterUnit
    theMeter.save()
    messages.add_message(request, messages.INFO, 'Meter {0} is changed.'.format(theMeter.meter_name), 'alert-success')
    return redirect(reverse('utilities:meter_list'))

class ListReadings(LoginRequiredMixin, generic.ListView):
    model = Reading
    template = 'utilities/reading_list.html'
