# -*- coding: utf-8 -*-
import datetime

from django.core.management import BaseCommand

from ... import app_settings
from ...initial_data import get_holidays_dictionary, get_holiday_type_list, \
    get_holidays_list
from ...models import ACPHoliday, HolidayType


class Command(BaseCommand):
    """
    To list the holidays:

    .. code-block:: bash

        $ python manage.py acp_holidays --list-initial

    You will get a print out like this. The [*] on the first column means that the initial data
    is already on the database.  The [-] on the first column means that the initial data
    is not on the database.

    .. code-block:: bash

        Year 2006  (11 holidays)
        ----------------------------------------------------------------------
        [*] año_nuevo                      2006-01-01
        [-] mártires                       2006-01-09
        [*] martes_carnaval                2006-02-28
        [*] viernes_santo                  2006-04-14
        [*] día_del_trabajo                2006-05-01

        ...

        ======================================================================
        Found 133 in initials
        Found 132 in database

    To export your the holidays currently in the database to a json file

    .. code-block:: bash

        $  python manage.py acp_holidays --export-holidays=/path/to/your/file.json
    """

    def add_arguments(self, parser):
        # parser.add_argument('optional-argument', nargs='?')
        parser.add_argument('--list-initial',
                            action='store_true',
                            dest='list_initial',
                            default=None,
                            help='List initial data')

        parser.add_argument('--export-holidays',
                            action='store',
                            dest='export_filename',
                            default=None,
                            help='Export holidays in database to json format')
        # parser.add_argument('--variable',
        #                     action='store',
        #                     dest='variable_name',
        #                     default=None,
        #                     help='Useful info')
        # parser.add_argument('--appended-argument',
        #                     action='append',
        #                     dest='appended_arg',
        #                     default=None,
        #                     help='Useful info')
        parser.add_argument('--update-initial',
                            action='store_true',
                            dest='update_initial',
                            default=None,
                            help='Update initial data')
        parser.add_argument('--update-initial-test',
                            action='store_true',
                            dest='update_initial_test',
                            default=None,
                            help='Update initial data (test only)')

    def handle(self, *args, **options):
        if options['list_initial']:
            self._list_initial_data()
        if options['export_filename']:
            self._export_holidays(options['export_filename'])
        if options['update_initial']:
            self._update_initial_data()
        if options['update_initial_test']:
            self._update_initial_data(test=True)

    def _export_holidays(self, filename):
        """
        Exports all ACPHoldays in the database to pretty pring json file in UTF-8 format.
        it exports the holidays in the format the initial_data need to load holidays:

            {
                "date": "2006-01-01",
                "holiday_type": "año_nuevo"
            },
            {
                "date": "2006-01-09",
                "holiday_type": "mártires"
            },
        ..

        :param filename: JSON file to save database content
        """

        db_holidays = ACPHoliday.objects.all().write_json(filename)
        self.stdout.write('Wrote %d holidays to %s' % (len(db_holidays), filename))

    def _list_initial_data(self):
        count_initial_holidays = 0
        count_db_holidays = 0

        ordered_holidays = get_holidays_dictionary()
        for year, holidays in ordered_holidays.items():
            self.stdout.write('Year %s  (%d holidays)' % (year, len(holidays)))
            self.stdout.write('-' * 70)
            for holiday in holidays:
                display = dict()
                display['found'] = '*'
                display['date'] = holiday['date']
                count_initial_holidays += 1
                try:
                    assert isinstance(holiday['holiday_type'], str), 'Holiday type should be a string'
                    short_name = holiday['holiday_type']
                    display['holiday_type'] = short_name
                    ACPHoliday.objects.get(holiday_type__short_name=short_name,
                                           date=holiday['date'])
                    count_db_holidays += 1
                except ACPHoliday.DoesNotExist:
                    display['found'] = '-'
                self.stdout.write('\t[{found}] {holiday_type:<30} {date}'.format(**display))
            self.stdout.write('=' * 70)
        self.stdout.write('Found %d in initials' % count_initial_holidays)
        self.stdout.write('Found %d in database' % count_db_holidays)

    def _update_initial_data(self, test=False):
        """Checks for updated holiday types and holidays from initial data and
        adds to database.

        @param: test: Set to True for tests. Will insert some test values and
                      will not write to actual database.
        @type: test: bool
        """
        if test:
            self.stdout.write("WARNING: Test flag is set, will use test data and not write to database.")
        self.stdout.write('Checking for updated HolidayType...')
        initial_holiday_types = get_holiday_type_list()
        if test:
            # Insert a test holiday type
            initial_holiday_types.append(
                {'name': 'TestHolidayType', 'short_name': 'test_holiday_type'})
        self.stdout.write(
            '{} HolidayType found.'.format(len(initial_holiday_types)))
        num_created = 0
        num_updated = 0
        num_skipped = 0
        for ht in initial_holiday_types:
            ht_name = ht.get('name', None)
            ht_short_name = ht.get('short_name', None)
            if not ht_short_name or not ht_name:
                num_skipped += 1
                self.stdout.write('Name or short_name missing: {}'.format(ht))
                continue

            qs = HolidayType.objects.filter(short_name=ht_short_name)
            if not qs.count():
                if not test:
                    HolidayType.objects.create(**ht)
                num_created += 1
                self.stdout.write(
                    'HolidayType {} created.'.format(ht_short_name))
            else:
                # Check if need to update name
                ht_obj = qs.first()
                if ht_obj.name != ht_name:
                    if not test:
                        ht_obj.name = ht_name
                        ht_obj.save()
                    num_updated += 1
                    self.stdout.write(
                        'HolidayType {} name updated to {}.'.format(
                            ht_short_name, ht_name))
        self.stdout.write(
            'HolidayType: {} created, {} updated, {} skipped.'.format(
                num_created, num_updated, num_skipped))

        # Check Holidays
        self.stdout.write('Checking for updated ACPHoliday...')
        holiday_list = get_holidays_list()
        if test:
            # Insert some test holidays
            holiday_list.append({
                "date": "2018-11-01",
                "holiday_type": "test_holiday_type"
            })
            holiday_list.append({
                "date": "2018-12-01",
                "holiday_type": "test_holiday_type"
            })
        self.stdout.write('{} holidays found.'.format(len(holiday_list)))
        num_created = 0
        num_updated = 0
        num_skipped = 0
        for h in holiday_list:
            h_date = h.get('date', None)
            h_short_name = h.get('holiday_type', None)
            # Check both fields have values
            if not h_date or not h_short_name:
                num_skipped += 1
                self.stdout.write('Missing date or holiday_type: {}'.format(h))
                continue
            # Parse date
            try:
                formatted_date = datetime.datetime.strptime(
                    h_date, app_settings.LOAD_DATE_FORMAT)
            except Exception as e:
                num_skipped += 1
                self.stdout.write(
                    'Error parsing date from {}. Exception: {}'.format(h, e))
                continue
            # Check holiday type
            try:
                h_type_obj = HolidayType.objects.get(short_name=h_short_name)
            except HolidayType.DoesNotExist:
                if not test:
                    num_skipped += 1
                    self.stdout.write(
                        'HolidayType {} does not exist. Data {}'.format(
                            h_short_name, h))
                    continue
                else:
                    pass
            # Check holidays
            qs = ACPHoliday.objects.filter(date=formatted_date)
            if qs.count():
                # If holiday exists, check if need to update HolidayType
                h_obj = qs.first()
                if h_obj.holiday_type.short_name != h_short_name:
                    if not test:
                        h_obj.holiday_type = h_type_obj
                        h_obj.save()
                    num_updated += 1
                    self.stdout.write(
                        'ACPHoliday {} updated to HolidayType {}'.format(
                            h_date, h_short_name))
            else:
                # Create a new Holiday
                if not test:
                    h_obj = ACPHoliday.objects.create(
                        date=formatted_date, holiday_type=h_type_obj)
                num_created += 1
                self.stdout.write(
                    'New ACPHoliday created: date: {} holiday_type: {}'.format(
                        h_date, h_short_name))
        self.stdout.write(
            'ACPHoliday: {} created, {} updated, {} skipped.'.format(
                num_created, num_updated, num_skipped))
