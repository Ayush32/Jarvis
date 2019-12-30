import json

from django.db import models

from . import app_settings


class ACPHolidayQuerySet(models.QuerySet):
    def write_json(self, filename):
        holidays = list()
        db_holidays = self
        for db_holiday in db_holidays:
            holiday_dict = dict()
            holiday_dict['date'] = db_holiday.date.strftime(app_settings.LOAD_DATE_FORMAT)
            holiday_dict['holiday_type'] = db_holiday.holiday_type.short_name
            holidays.append(holiday_dict)

        with open(filename, 'w', encoding='utf-8') as outfile:
            json.dump(holidays, outfile, indent=4, ensure_ascii=False)

        return self


class ACPHolidayManager(models.Manager):
    def get_queryset(self):
        return ACPHolidayQuerySet(self.model, using=self._db)

    def update_fiscal_years(self):
        from .models import FiscalYear
        holidays_without_fiscal_year = self.filter(fiscal_year=0)
        for holiday in holidays_without_fiscal_year:
            fy = FiscalYear.create_from_date(holiday.date)
            holiday.fiscal_year = fy.year
            holiday.save()
        return holidays_without_fiscal_year
