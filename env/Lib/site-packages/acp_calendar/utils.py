from datetime import datetime

from . import app_settings
from .initial_data import get_holidays_list
from .models import ACPHoliday


def compare_initial_data_against_db(initial_data_json=None):
    """
    This method compares the holidays in holiday_initial_data.json to the content of the database
    :param initial_data_json: String with filename of json file
    :return: list of dictionaries containing date and holiday_type of holidays that are not the database
    """
    holidays = get_holidays_list(initial_data_json)
    not_found = list()
    for holiday in holidays:
        try:
            ACPHoliday.objects.get(date=datetime.strptime(holiday['date'], app_settings.LOAD_DATE_FORMAT))
        except ACPHoliday.DoesNotExist:
            not_found.append(holiday)
    return not_found
