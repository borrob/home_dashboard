"""
Defining the utilities URL links and their respones.
"""
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.conf import settings
from django.core.paginator import EmptyPage, Paginator
from django.db import IntegrityError
from django.utils.datastructures import MultiValueDictKeyError
from django.shortcuts import render, redirect, reverse

from .forms import NewMeterForm, ReadingForm
from .models import Meter, Reading, Usage


# METER
@login_required()
def show_meters(request):
    """
    Render the page with the meters.

    Keeping on eye on the sorting list and the paging.

    :param request: the user http request
    :return: the html page with the meters as a http response
    """
    # Get the sort_key from the session
    sort_key = request.session.get('meterlist_sort_by', None)
    # Override with the sort_key that the user iq requesting.
    try:
        sort_key_request = request.GET['sort_by']
        sort_key = sort_key_request if sort_key != sort_key_request else '-' + sort_key_request
    except MultiValueDictKeyError:
        sort_key = sort_key if sort_key else 'id'

    request.session['meterlist_sort_by'] = sort_key
    queryset = Meter.objects.order_by(sort_key)

    # deal with paging
    try:
        page_id = int(request.GET.get('page', 1))
    except ValueError:
        # catching if 'page' is not an integer
        page_id = 1
    paginator = Paginator(queryset, settings.PAGE_SIZE)
    page_id = paginator.num_pages if page_id > paginator.num_pages else page_id
    try:
        page = paginator.page(page_id)
    except EmptyPage:
        page_id = 1
        page = paginator.page(page_id)

    return render(request,
                  'utilities/meter_list.html',
                  {'object_list': page, 'current_page': page_id})


@login_required()
def meter(request, meter_id=None):
    """
    Add or edit a meter.
    """
    if request.method == 'POST' and not request.POST.get('_method', 'not_put') == 'PUT':
        if request.user.has_perm('utilities.add_meter'):
            _add_new_meter_from_request(request)
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Missing permission to add meter, please login',
                                 'alert-danger')
        return redirect(reverse('utilities:meter_list'))

    if request.method == 'POST' and request.POST.get('_method', 'not_put') == 'PUT':
        if request.user.has_perm('utilities.change_meter'):
            _change_meter_from_request(request)
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Missing permission to edit meter, please login.',
                                 'alert-danger')

        return redirect(reverse('utilities:meter_list'))

    # Default to GET
    form = NewMeterForm()
    edit = False
    if meter_id:
        try:
            meter_to_edit = Meter.objects.get(pk=meter_id)
        except Meter.DoesNotExist:
            pass
        else:
            form = NewMeterForm(initial={'meter_name': meter_to_edit.meter_name,
                                         'meter_unit': meter_to_edit.meter_unit})
            edit = True

    return render(request,
                  'utilities/meter_form.html',
                  {'form': form, 'edit': edit, 'm_id': meter_id})


def _add_new_meter_from_request(request):
    """
    Add a new meter form the post data of this request. Does **NOT** check permission.

    :param request: the user http request with the info on the new meter.
    :return: nothing
    """
    form = NewMeterForm(request.POST)
    if form.is_valid():
        try:
            new_meter = Meter.objects.create(meter_name=form.cleaned_data['meter_name'],
                                             meter_unit=form.cleaned_data['meter_unit'])
            new_meter.save()
        except IntegrityError:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Meter name is already taken. Cannot add a double entry.',
                                 'alert-danger')
        else:
            messages.add_message(request,
                                 messages.INFO,
                                 'Meter {0} is added.'.format(new_meter.meter_name),
                                 'alert-success')
    else:
        messages.add_message(request,
                             messages.ERROR,
                             form.errors.get(list(form.errors.keys())[0])[0],
                             'alert-danger')


def _change_meter_from_request(request):
    """
    Change a meter with the data from the user request. Does **NOT** check permissions.

    The entire information set of the meter should be supplied.

    :param request: the user http request with the relevant data
    :return: nothing
    """
    form = NewMeterForm(request.POST)
    messages.error(request, "Woot!")
    try:
        meter_to_change = Meter.objects.get(pk=form.data.get('id'))
    except (KeyError, Meter.DoesNotExist):
        messages.add_message(request,
                             messages.ERROR,
                             'Something went wrong with getting the old meter.',
                             'alert-danger')
    else:
        meter_to_change.full_clean()
        try:
            meter_to_change.meter_name = form.cleaned_data['meter_name']
            if Meter.objects.filter(meter_name=meter_to_change.meter_name).exclude(pk=meter_to_change.id).count() != 0:
                raise IntegrityError
        except (IntegrityError, KeyError):
            messages.add_message(request,
                                 messages.ERROR,
                                 'Meter name is already taken. Cannot add a double entry.',
                                 'alert-danger')
        except (KeyError, AttributeError):
            pass
        else:
            try:
                meter_to_change.meter_unit = form.cleaned_data['meter_unit']
            except (KeyError, AttributeError):
                pass

            meter_to_change.save()
            #TODO check inbouwen of meter al bestaat
            messages.add_message(request,
                                 messages.ERROR,
                                 'Meter {0} is changed.'.format(meter_to_change.meter_name),
                                 'alert-success')
    print('message from change meter: ', messages)
    print('')
    messages.add_message(request, messages.ERROR,'sf')


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
        # pylint: disable=unused-variable
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


# READINGS
@login_required
def list_readings(request):
    """
    Show all the readings.
    """
    try:
        readings = Reading.objects.all()
        if request.GET.get('m_id'):
            readings = readings.filter(meter_id=request.GET.get('m_id'))
    except Reading.DoesNotExist:
        readings = []

    # Get the sort_key from the session
    sort_key = request.session.get('readinglist_sort_by')
    # Override with the sort_key that the user iq requesting.
    try:
        sort_key_request = request.GET['sort_by']
        sort_key = sort_key_request if sort_key != sort_key_request else '-'+sort_key_request
    except MultiValueDictKeyError:
        sort_key = sort_key if sort_key else 'id'

    request.session['readinglist_sort_by'] = sort_key
    readings = readings.order_by(sort_key)

    # deal with paging
    try:
        page_id = int(request.GET.get('page', 1))
    except ValueError:
        # catching if 'page' is not an integer
        page_id = 1
    paginator = Paginator(readings, settings.PAGE_SIZE)
    page_id = paginator.num_pages if page_id > paginator.num_pages else page_id
    try:
        page = paginator.page(page_id)
    except EmptyPage:
        page_id = 1
        page = paginator.page(page_id)

    meters = Meter.objects.all()

    return render(request,
                  'utilities/reading_list.html',
                  {'readings': page,
                   'current_page': page_id,
                   'meters': meters})


@login_required()
def reading(request, reading_id=None):
    """
    Add (or edit) a reading and store it into the database.

    Note: when saving a reading, the usage is calculated automatically.
    :param request: the user http request
    :param int reading_id: the id of the reading to edit, defauts to 'None' and can be left blank
                           when adding a new meter.
    :return: html page with the form to add/edit the reading
    """
    if request.method == 'POST' and not request.POST.get('_method', 'not_put') == 'PUT':
        return _process_new_reading(request)

    if request.method == 'POST' and request.POST.get('_method', 'not_put') == 'PUT':
        return _process_edit_reading(request)

    # Default to GET: show the form
    return _process_show_reading_form(reading_id, request)


def _process_show_reading_form(reading_id, request):
    """
    Initialise the reading form with either an empty reading or the specified reading.

    :param reading_id: if used, the id of the reading to edit (can be left None)
    :param request: the user http request
    :return: renderd html form to add/edit a reading
    """
    form = ReadingForm()
    edit = False
    if reading_id:
        try:
            reading_to_edit = Reading.objects.get(pk=reading_id)
        except Reading.DoesNotExist:
            pass
        else:
            form = ReadingForm(instance=reading_to_edit)
            edit = True
    return render(request,
                  'utilities/reading_form.html',
                  {'form': form, 'edit': edit, 'r_id': reading_id})


def _process_edit_reading(request):
    """
    Process the action that the users wants to edit an existing reading.

    :param request: the user http request
    :return: render the form page with the data of the specified reading
    """
    if request.user.has_perm('utilities.change_reading'):
        _change_reading_from_request(request)
    else:
        messages.add_message(request,
                             messages.ERROR,
                             'Missing permission to edit reading, please login.',
                             'alert-danger')
    return redirect(reverse('utilities:reading_list'))


def _process_new_reading(request):
    """
    Process the action that the users wants to add a new reading.

    :param request: the http request from the user
    :return: render the form page
    """
    if request.user.has_perm('utilities.add_reading'):
        _add_new_reading_from_request(request)
    else:
        messages.add_message(request,
                             messages.ERROR,
                             'Missing permission to add a reading, please login',
                             'alert-danger')
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
        # pylint: disable=unused-variable
        reading_to_delete = Reading.objects.get(pk=reading_id)
        (deleted, deleted_reading) = reading_to_delete.delete()
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


def _add_new_reading_from_request(request):
    """
    Add a new reading form the post data of this request. Does **NOT** check permission.

    :param request: the user http request with the info on the new meter.
    :return: nothing
    """
    form = ReadingForm(request.POST)
    if form.is_valid():
        form.save()
        messages.add_message(request,
                             messages.INFO,
                             'Reading is added.',
                             'alert-success')
    else:
        messages.add_message(request,
                             messages.ERROR,
                             'Missing key element to add a new reading.',
                             'alert-danger')


def _change_reading_from_request(request):
    """
    Change a meter with the data from the user request. Does **NOT** check permissions.

    :param request: the user http request with the relevant data
    :return: nothing
    """
    try:
        reading_to_change = Reading.objects.get(pk=request.POST['id'])
    except (KeyError, Reading.DoesNotExist):
        messages.add_message(request,
                             messages.ERROR,
                             'Something went wrong with getting the old reading.',
                             'alert-danger')
    else:
        form = ReadingForm(request.POST, instance=reading_to_change)
        if form.is_valid():
            form.save()
        else:
            messages.add_message(request,
                                 messages.ERROR,
                                 'Missing key element to change the reading.',
                                 'alert-danger')


# USAGES
@login_required
def list_usages(request):
    """
    Show all the usages of the readings.

    TODO: make selection of meter, data, ...
    """
    # Get the sort_key from the session
    sort_key = request.session.get('usagelist_sort_by')
    # Override with the sort_key that the user iq requesting.
    try:
        sort_key_request = request.GET['sort_by']
        sort_key = sort_key_request if sort_key != sort_key_request else '-'+sort_key_request
    except MultiValueDictKeyError:
        sort_key = sort_key if sort_key else 'id'

    request.session['usagelist_sort_by'] = sort_key

    try:
        usages = Usage.objects.all()
        if request.GET.get('m_id'):
            usages = usages.filter(meter_id=request.GET.get('m_id'))
        if sort_key[-4:] == 'date':
            order = '-' if sort_key[:1] == '-' else ''
            usages = usages.order_by(order + 'year', order + 'month')
        else:
            usages = usages.order_by(sort_key)
    except Usage.DoesNotExist:
        usages = []

    # deal with paging
    try:
        page_id = int(request.GET.get('page', 1))
    except ValueError:
        # catching if 'page' is not an integer
        page_id = 1
    paginator = Paginator(usages, settings.PAGE_SIZE)
    page_id = paginator.num_pages if page_id > paginator.num_pages else page_id
    try:
        page = paginator.page(page_id)
    except EmptyPage:
        page_id = 1
        page = paginator.page(page_id)

    meters = Meter.objects.all()

    return render(request,
                  'utilities/usage_list.html',
                  {'usages': page,
                   'current_page': page_id,
                   'meters': meters})
