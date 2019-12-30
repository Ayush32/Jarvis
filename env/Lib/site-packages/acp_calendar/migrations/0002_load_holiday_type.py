# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from ..initial_data import load_data


class Migration(migrations.Migration):
    dependencies = [
        ('acp_calendar', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_data)
    ]
