"""
Defining the utilities URL links and their respones.
"""
from datetime import datetime
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.datastructures import MultiValueDictKeyError
from django.views import generic
from django.shortcuts import render, redirect, reverse

from .models import Meter, Reading, Usage, update_usage_after_new_reading

#METER
class ListMeters(LoginRequiredMixin, generic.ListView): # pylint: disable=too-many-ancestors
    """
    Show a list of all the meters.

    TODO: add paging
    TODO: add selecting of specific meter
    TODO: add selection of specific year/month
    """
    model = Meter
    template = 'utilities/meter_list.html'

@permission_required('utilities.add_meter')
def add_meter(request):
    """
    Add a meter.
    """
    try:
        meter_name = request.POST.get('meter_name')
        meter_unit = request.POST.get('unit_name')
    except KeyError:
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to add a new meter.',
                             'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    if(meter_name is None or meter_unit is None):
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to add a new meter.',
                             'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    try:
        Meter.objects.get(meter_name=meter_name)
    except Meter.DoesNotExist:
        #meter doesn't exist -> OK!
        pass
    else:
        messages.add_message(request,
                             messages.ERROR,
                             'Meter already exists. Cannot add a double entry.',
                             'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    new_meter = Meter.objects.create(meter_name=meter_name, meter_unit=meter_unit)
    new_meter.save()
    messages.add_message(request,
                         messages.INFO,
                         'Meter {0} is added.'.format(new_meter.meter_name),
                         'alert-success')
    return redirect(reverse('utilities:meter_list'))

@permission_required('utilities.delete_meter')
def delete_meter(request):
    """
    Delete a meter
    """
    try:
        meter_name = request.POST.get('meter_name')
    except KeyError:
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to delete meter.',
                             'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    if meter_name is None:
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to delete meter.',
                             'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    deleted = 0
    try:
        #pylint: disable=unused-variable
        (deleted, deleted_meter) = Meter.objects.get(meter_name=meter_name).delete()
    except Meter.DoesNotExist:
        messages.add_message(request,
                             messages.ERROR,
                             'Cannot delete already deleted meter.',
                             'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    if deleted >= 1:
        messages.add_message(request,
                             messages.INFO,
                             'Meter {0} is deleted'.format(meter_name),
                             'alert-success')
        return redirect(reverse('utilities:meter_list'))

    messages.add_message(request,
                         messages.ERROR,
                         'Cannot delete already deleted meter.',
                         'alert-danger')
    return redirect(reverse('utilities:meter_list'))

@permission_required('utilities.change_meter')
def edit_meter(request):
    """
    Edit a meter.
    """
    try:
        meter_name = request.POST.get('meter_name')
        new_name = request.POST.get('new_name')
        meter_unit = request.POST.get('unit_name')
    except KeyError:
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to change a meter.',
                             'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    if(meter_name is None or meter_unit is None):
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to change a meter.',
                             'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    try:
        edited_meter = Meter.objects.get(meter_name=meter_name)
    except Meter.DoesNotExist:
        messages.add_message(request,
                             messages.ERROR,
                             'Cannot change a meter that doesn\'t exist yet.',
                             'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    try:
        namecheck_meter = Meter.objects.get(meter_name=new_name)
    except Meter.DoesNotExist:
        #new name isn't taken -> OK!
        pass
    else:
        if namecheck_meter.pk != edited_meter.pk:
            #just changing the unit name
            messages.add_message(request,
                                 messages.ERROR,
                                 'Name is already taken',
                                 'alert-danger')
            return redirect(reverse('utilities:meter_list'))

    edited_meter.meter_name = new_name
    edited_meter.unit_name = meter_unit
    edited_meter.save()
    messages.add_message(request,
                         messages.INFO,
                         'Meter {0} is changed.'.format(edited_meter.meter_name),
                         'alert-success')
    return redirect(reverse('utilities:meter_list'))

#READINGS
@login_required
def list_readings(request):
    """
    Show all the readings.
    TODO: add paging.
    """
    try:
        readings = Reading.objects.all()
        if request.GET.get('m_id') or request.session.get('show_meter'):
            meter_filter = int(request.GET.get('m_id', request.session.get('show_meter')))
            if meter_filter >= 0:
                request.session['show_meter']=meter_filter
                readings = readings.filter(meter_id=meter_filter)
            else:
                request.session['show_meter']=None
    except Reading.DoesNotExist:
        pass

    meters = Meter.objects.all()
    return render(request,
                  'utilities/reading_list.html',
                  {'object_list': readings,
                   'meters': meters})

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
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to add a new reading.',
                             'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    if(meter is None or reading_date is None or reading_number is None):
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to add a new reading.',
                             'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    try:
        meter = Meter.objects.get(pk=meter)
    except Meter.DoesNotExist:
        messages.add_message(request,
                             messages.ERROR,
                             'Unknown meter',
                             'alert-danger')
        return redirect(reverse('utilities:reading_list'))
    else:
        new_reading = Reading.objects.create(meter=meter,
                                             reading=reading_number,
                                             date=datetime.\
                                                  strptime(reading_date, '%Y-%m-%d').\
                                                  date(),
                                             remark=remark)
        new_reading.save()
        update_usage_after_new_reading(new_reading)
    messages.add_message(request,
                         messages.INFO,
                         '{0} is added.'.format(new_reading),
                         'alert-success')
    return redirect(reverse('utilities:reading_list'))

@permission_required('utilities.delete_reading')
def delete_reading(request):
    """
    Delete a meter reading.
    """
    try:
        reading_id = int(request.POST.get('reading_id'))
    except KeyError:
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to delete reading.',
                             'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    if reading_id is None:
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to delete reading.',
                             'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    deleted = 0
    try:
        #pylint: disable=unused-variable
        reading_to_delete = Reading.objects.get(pk=reading_id)
        (deleted, deleted_reading) = reading_to_delete.delete()
        update_usage_after_new_reading(reading_to_delete)
    except Reading.DoesNotExist:
        messages.add_message(request,
                             messages.ERROR,
                             'Cannot delete already deleted reading.',
                             'alert-danger')
        return redirect(reverse('utilities:reading_list'))
    if deleted >= 1:
        messages.add_message(request,
                             messages.INFO,
                             'Reading is deleted',
                             'alert-success')
        return redirect(reverse('utilities:reading_list'))

    messages.add_message(request,
                         messages.ERROR,
                         'Cannot delete already deleted reading.',
                         'alert-danger')
    return redirect(reverse('utilities:reading_list'))

@permission_required('utilities.change_reading')
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
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to change the reading.',
                             'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    if(meter is None or reading_date is None or reading_number is None):
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to change the reading.',
                             'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    try:
        meter = Meter.objects.get(pk=meter)
    except Meter.DoesNotExist:
        messages.add_message(request,
                             messages.ERROR,
                             'Unknown meter',
                             'alert-danger')
        return redirect(reverse('utilities:reading_list'))

    edited_reading = Reading.objects.get(pk=reading)
    edited_reading.meter = meter
    edited_reading.reading = reading_number
    edited_reading.date = datetime.strptime(reading_date, '%Y-%m-%d').date()
    edited_reading.remark = remark
    edited_reading.save()
    update_usage_after_new_reading(edited_reading)

    messages.add_message(request,
                         messages.INFO,
                         '{0} is changed.'.format(edited_reading),
                         'alert-success')
    return redirect(reverse('utilities:reading_list'))

@login_required
def list_usages(request):
    """
    Show all the usages of the readings.
    TODO: add paging
    TODO: make selection of meter, data, ...
    TODO: add sorting
    """
    try:
        usages = Usage.objects.all()
        if request.GET.get('m_id'):
            usages = usages.filter(meter_id=request.GET.get('m_id'))
    except Usage.DoesNotExist:
        pass

    meters = Meter.objects.all()

    return render(request, 'utilities/usage_list.html', {'object_list': usages, 'meters': meters})
