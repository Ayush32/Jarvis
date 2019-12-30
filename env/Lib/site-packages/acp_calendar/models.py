# -*- coding: utf-8 -*-
from calendar import monthrange, IllegalMonthError
from datetime import timedelta, date, datetime

from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from . import app_settings
from .exceptions import ACPCalendarException
from .managers import ACPHolidayManager


class FiscalYear(object):
    """
    This class represents a Pancama Canal Fiscal year which start on October first
    of the previous year and ends on September 30th of the current year.
    For example fiscal year 2016 starts on October 1st, 2015 and ends September 30th
    2016
    """

    def __init__(self, year, **kwargs):
        """
        Contructor for Fiscal year.

        :param year: Fiscal year
        :param kwargs: includes display wich is the template for the str method and
        length which is also used in the str method
        """
        self.year = year
        self.start_date = date(year - 1, 10, 1)
        self.end_date = date(year, 9, 30)
        self.fy_format = {'display': kwargs.get('display', 'FY%s'),
                          'length': kwargs.get('length', 2)}

    def __str__(self):
        return self.fy_format['display'] % str(self.year)[self.fy_format['length']:]

    def months_in_fiscal_year(self):
        """
        Gets a tuple of tuple containing the month number and the year of the months in the
        fiscal year.

        :return: a tuple containing 12 tuples. Each tuple contains 2 integer, the first one is the month the
        second one is the year.
        """
        return ((10, self.year - 1), (11, self.year - 1), (12, self.year - 1),
                (1, self.year), (2, self.year), (3, self.year), (4, self.year),
                (5, self.year), (6, self.year), (7, self.year), (8, self.year),
                (9, self.year))

    @staticmethod
    def create_from_date(cdate, **kwargs):
        """
        Creates a Fiscal year object for a date.

        :param cdate: Date or datetime object within the fiscal year
        :param kwargs: Same kwargs as for the constructor
        :return: a FiscalYear object
        """
        if isinstance(cdate, datetime):
            cdate = cdate.date()
        start_of_fy = date(cdate.year, 10, 1)
        if cdate >= start_of_fy:
            year = cdate.year + 1
        else:
            year = cdate.year
        return FiscalYear(year, **kwargs)

    @staticmethod
    def current_fiscal_year(**kwargs):

        """
        Create a fiscal year object for current date
        :param kwargs: Same kwargs as for the constructor
        :return: FiscalYear object for current date
        """
        cdate = timezone.now()
        return FiscalYear.create_from_date(cdate, **kwargs)


class HolidayType(models.Model):
    """
    Model for Holiday type.

    .. code-block::python

        holiday = Holiday.objects.create(name='Christmas', short_name='xmas')
    """
    name = models.CharField(_('Holiday name'), max_length=60)
    short_name = models.CharField(_('short name'), max_length=60, unique=True)

    def __str__(self):
        return self.name


class ACPHoliday(models.Model):
    """
    Model for a non working day in the Panama Canal due to a holiday. This model contains all the logic for the
    working days calculations.
    """
    date = models.DateField(_('Date'), unique=True)
    holiday_type = models.ForeignKey(HolidayType, verbose_name=_('Holiday type'))
    fiscal_year = models.IntegerField(_('fiscal year'), default=0)

    def __str__(self):
        return '{0} {1}'.format(self.date.strftime(app_settings.DATE_FORMAT), self.holiday_type)

    class Meta:
        ordering = ('date',)

    objects = ACPHolidayManager()

    @staticmethod
    def validate_dates(start_date, end_date):
        """
        Validates three rules:
        1. End date is not before start date
        2. End date cannot occur after oldest holiday in database
        3. Start date cannot occur before the first holiday in database

        Will raise an ACPCalendarException if one of these rules is broken.

        :param start_date: Start date
        :param end_date: End date
        """
        if start_date > end_date:
            raise ACPCalendarException(_('Start date cannot occur after end date'))
        last_holiday = ACPHoliday.objects.all().last()
        if end_date > last_holiday.date:
            raise ACPCalendarException(_('End date exceed the last registered holiday'))
        first_holiday = ACPHoliday.objects.all().first()
        if start_date < first_holiday.date:
            raise ACPCalendarException(_('Start date precedes the first registered holiday'))

    @staticmethod
    def get_working_days(start_date, end_date, **kwargs):
        """
        Calculates the amount of working days between start date and end date. It will calculate all days that are not
        saturday or sunday and then substract the holiday in the range if they exist.

        :param start_date:
        :param end_date:
        :param kwargs:
        :return: Number of working days between the star date and the end date
        """
        start_date = ACPHoliday.convert_to_date(start_date)
        end_date = ACPHoliday.convert_to_date(end_date)
        ACPHoliday.validate_dates(start_date, end_date)
        day_generator = ACPHoliday.days_in_range_generator(start_date, end_date)
        holidays_in_range = ACPHoliday.objects.filter(date__gte=start_date, date__lte=end_date).count()
        working_days = sum(1 for day in day_generator if day.weekday() < 5)
        return working_days - holidays_in_range

    @staticmethod
    def convert_to_date(study_date):
        """
        Converts String to date to a date object.

        :param study_date: date to be processed
        :return: date object
        """
        if isinstance(study_date, str):
            try:
                date_object = datetime.strptime(study_date, app_settings.DATE_FORMAT).date()
                return date_object
            except ValueError as e:
                raise ACPCalendarException(str(e))
        elif isinstance(study_date, date):
            return study_date
        else:
            raise ACPCalendarException('Dates must be either string or date objects')

    @staticmethod
    def days_in_range_generator(start_date, end_date):
        """
        Creates a generator that contains all date dates between start_date and end_date

        :param start_date: Start date in string or date
        :param end_date: End date in string or date
        :return: A generator containing all dates in range
        """
        start_date = ACPHoliday.convert_to_date(start_date)
        end_date = ACPHoliday.convert_to_date(end_date)
        start_date = start_date - timedelta(1)
        day_generator = (start_date + timedelta(x + 1) for x in range((end_date - start_date).days))
        return day_generator

    @staticmethod
    def week_end_days(start_date, end_date):
        start_date = ACPHoliday.convert_to_date(start_date)
        end_date = ACPHoliday.convert_to_date(end_date)
        day_generator = ACPHoliday.days_in_range_generator(start_date, end_date)
        week_end_days = sum(1 for day in day_generator if day.weekday() >= 5)
        return week_end_days

    @staticmethod
    def working_delta(start_date, working_days):
        """
        Calculates the date based on a start date and the number of working days in the future

        :param start_date: Start date
        :param working_days: Number of woking days to the date we are interested
        :return: Date that is n working days from start date.
        """
        start_date = ACPHoliday.convert_to_date(start_date)
        working_days = int(working_days)
        first_guess = working_days + working_days / 5 * 2 + 4
        end_date = start_date + timedelta(days=first_guess)
        holidays = ACPHoliday.objects.filter(date__gte=start_date, date__lte=end_date)
        holiday_list = list()
        for holiday in holidays:
            holiday_list.append(holiday.date)
        not_completed = True
        end_date = start_date
        count = 0
        while not_completed:
            if end_date.weekday() < 5 and end_date not in holiday_list:
                count += 1
            if working_days == count:
                break
            end_date = end_date + timedelta(days=1)
        return end_date

    @staticmethod
    def get_working_days_for_month(year, month):
        """
        Calculate the amount of working days in a month

        :param year: Year
        :param month: month
        :return: Number of working days
        """
        try:
            last_day_of_month = monthrange(year, month)[1]
            start_date = date(year, month, 1)
            end_date = date(year, month, last_day_of_month)

            return ACPHoliday.get_working_days(start_date, end_date)
        except IllegalMonthError as e:
            raise ACPCalendarException(str(e))
