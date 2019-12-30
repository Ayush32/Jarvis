from django import forms
from django.utils.translation import ugettext_lazy as _


class CalculatorForm(forms.Form):
    start_date = forms.DateField(label=_('Start date'))
    end_date = forms.DateField(label=_('End date'))
