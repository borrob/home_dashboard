"""
Business logic for the utilities app.
"""
from datetime import date
import logging

from utilities.exceptions import MeterError
from utilities.models import Usage, Reading

LOGGER = logging.getLogger('home_dashboard_log')


def update_usage_after_new_reading(reading): #pylint: disable=too-many-locals
    """
    A new reading is inserted, so try and calculate the new montly usage.
    """
    LOGGER.debug(f'Going to update the useage with reading: {reading}.')
    last_reading_before = get_readings_before_or_after(reading.date, reading.meter, 'before')
    last_reading_before = last_reading_before if last_reading_before else reading
    first_reading_after = get_readings_before_or_after(reading.date, reading.meter, 'after')
    first_reading_after = first_reading_after if first_reading_after else reading

    month_before = last_reading_before.date.month
    year_before = last_reading_before.date.year
    month_after = first_reading_after.date.month
    year_after = first_reading_after.date.year

    #clean up
    Usage.objects.filter(year__gte=year_before, month__gte=month_before).\
        filter(year__lte=year_after, month__lte=month_after).\
        filter(meter=reading.meter).\
        delete()

    #calculate new usages
    for year in range(year_before, year_after+1):
        for month in range(1, 12+1):
            if year == year_before and month < month_before:
                pass
            elif year == year_after and month > month_after:
                pass
            else:
                month_date_1 = date(year, month, 1)
                if month == 12:
                    month_date_31 = date(year+1, 1, 1)
                else:
                    month_date_31 = date(year, month+1, 1)

                try:
                    r_before1 = Reading.objects.filter(meter=reading.meter).\
                                    filter(date__lte=month_date_1).\
                                    order_by('-date')[0]
                    r_after1 = Reading.objects.filter(meter=reading.meter).\
                                    filter(date__gt=month_date_1).\
                                    order_by('date')[0]
                    r_before31 = Reading.objects.filter(meter=reading.meter).\
                                    filter(date__lt=month_date_31).\
                                    order_by('-date')[0]
                    r_after31 = Reading.objects.filter(meter=reading.meter).\
                                    filter(date__gte=month_date_31).\
                                    order_by('date')[0]
                except IndexError:
                    LOGGER.warning(f'Could not calculate the usage for meter {reading.meter}, '
                                   f'{year}-{month}')
                else:
                    first_of_month = calculate_reading_on_date(month_date_1, r_before1, r_after1)
                    last_of_month = calculate_reading_on_date(month_date_31, r_before31, r_after31)

                    use = last_of_month - first_of_month
                    usage = Usage.objects.create(meter=reading.meter,
                                                 month=month,
                                                 year=year,
                                                 usage=use)
                    usage.save()
                    LOGGER.debug(f'Caculated new useage: {usage}')


def get_readings_before_or_after(the_date, meter, before_after):
    """
    Get the first reading before and first reading after this date.

    This method does not generate an exception, but returns none if the reading
    before or after does not exists.

    TODO: add testing!
    """
    reading = None
    if before_after == 'before':
        try:
            reading = Reading.objects.filter(meter=meter).\
                      filter(date__lt=the_date).\
                      order_by('-date')[0]
        except (Reading.DoesNotExist, IndexError):
            pass
    elif before_after == 'after':
        try:
            reading = Reading.objects.filter(meter=meter).\
                      filter(date__gt=the_date).\
                      order_by('date')[0]
        except (Reading.DoesNotExist, IndexError):
            pass

    return reading


def calculate_reading_on_date(the_date, reading_1, reading_2):
    """
    Calculate the useage on the_date based on the the input readings.

    Raises errors when something is not good.
    """
    LOGGER.debug(f'Calling calculate_reading_on_date for {the_date} with {reading_1} and '
                 f'{reading_2}')
    if reading_1.meter != reading_2.meter:
        raise MeterError('Meters are not equal, cannot calculate usegage.')
    if reading_1.date == reading_2.date:
        return reading_1.reading
    if reading_1.date > reading_2.date:
        # making sure 1 is before 2
        reading_1, reading_2 = reading_2, reading_1
    if the_date < reading_1.date or the_date > reading_2.date:
        raise ValueError('The specified date is not between the dates of the readings.')

    days_between_readings = (reading_2.date - reading_1.date).days
    days_since_reading_1 = (the_date - reading_1.date).days
    usage_between_reading = reading_2.reading - reading_1.reading
    reading_on_date = reading_1.reading \
                      + usage_between_reading \
                      * days_since_reading_1/days_between_readings
    return reading_on_date
