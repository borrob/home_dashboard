from decimal import *

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

@login_required
def list_readings(request):
    """
    Show all the readings.
    TODO: add paging.
    """
    try:
        readings = Reading.objects.all()
    except DoesNotExist:
        pass

    meters = Meter.objects.all()
    return render(request, 'utilities/reading_list.html', {'object_list': readings, 'meters': meters})

@permission_required('utilities.add_reading')
def add_reading(request):
    """
    Add a reading.
    """
    try:
        meter = int(request.POST.get('meter_id'))
        reading_date = request.POST.get('reading_date')
        reading_number = Decimal(request.POST.get('reading'))
        remark = request.POST.get('remark')
    except (KeyError, TypeError):
        messages.add_message(request, messages.ERROR, 'Missing key element to add a new reading.', 'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    if(meter == None or reading_date == None or reading_number == None):
        messages.add_message(request, messages.ERROR, 'Missing key element to add a new reading.', 'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    try:
        meter = Meter.objects.get(pk=meter)
    except Meter.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'Unknown meter', 'alert-danger')
        return redirect(reverse('utilities:reading_list'))
    else:
        r = Reading.objects.create(
                meter = meter,
                reading = reading_number,
                date = reading_date,
                remark = remark)
        r.save()
    messages.add_message(request, messages.INFO, '{0} is added.'.format(r), 'alert-success')
    return redirect(reverse('utilities:reading_list'))

@permission_required('utilities.delete_reading')
def delete_reading(request):
    """
    Delete a meter reading.
    """
    try:
        reading_id = int(request.POST.get('reading_id'))
    except KeyError:
        messages.add_message(request, messages.ERROR, 'Missing key element to delete reading.', 'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    if(reading_id == None):
        messages.add_message(request, messages.ERROR, 'Missing key element to delete reading.', 'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    deleted = 0
    try:
        (deleted, deletedReading) = Reading.objects.get(pk=reading_id).delete()
    except Reading.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'Cannot delete already deleted reading.', 'alert-danger')
        return redirect(reverse('utilities:reading_list'))
    if (deleted>=1):
        messages.add_message(request, messages.INFO, 'Reading is deleted', 'alert-success')
        return redirect(reverse('utilities:reading_list'))
    else:
        messages.add_message(request, messages.ERROR, 'Cannot delete already deleted reading.', 'alert-danger')
        return redirect(reverse('utilities:reading_list'))

@permission_required('utilities.edit_reading')
def edit_reading(request):
    """
    Edit a reading.
    """
    try:
        reading = int(request.POST.get('reading_id'))
        meter = int(request.POST.get('meter_id'))
        reading_date = request.POST.get('reading_date')
        reading_number = Decimal(request.POST.get('reading'))
        remark = request.POST.get('remark')
    except (KeyError, TypeError):
        messages.add_message(request, messages.ERROR, 'Missing key element to change the reading.', 'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    if(meter == None or reading_date == None or reading_number == None):
        messages.add_message(request, messages.ERROR, 'Missing key element to change the reading.', 'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    try:
        meter = Meter.objects.get(pk=meter)
    except Meter.DoesNotExist:
        messages.add_message(request, messages.ERROR, 'Unknown meter', 'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    r = Reading.objects.get(pk=reading)
    r.meter = meter
    r.reading = reading_number
    r.date = reading_date
    r.remark = remark
    r.save()

    messages.add_message(request, messages.INFO, '{0} is changed.'.format(r), 'alert-success')
    return redirect(reverse('utilities:reading_list'))
