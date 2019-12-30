import os


# noinspection PyPep8Naming
class AppSettings(object):
    def __init__(self, prefix):
        self.prefix = prefix

    def _settings(self, settings_name, default_value):
        from django.conf import settings
        return getattr(settings, self.prefix + settings_name, default_value)

    @property
    def DATE_FORMAT(self):
        return self._settings('DATE_FORMAT', '%Y-%m-%d')

    @property
    def LOAD_DATE_FORMAT(self):
        """
        This is the date forma for the initial data load. I you change this the date format in
        holiday_initial_data.json must be changed

        :return: String with date format
        """
        return '%Y-%m-%d'

    @property
    def INITIAL_DATA_FILENAME(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        data_filename = os.path.join(dir_path, 'holiday_initial_data.json')
        return self._settings('INITIAL_DATA_FILENAME', data_filename)


# Ugly? Guido recommends this himself ...
# http://mail.python.org/pipermail/python-ideas/2012-May/014969.html
import sys  # noqa

app_settings = AppSettings('ACP_CALENDAR_')
app_settings.__name__ = __name__
sys.modules[__name__] = app_settings
