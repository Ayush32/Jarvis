from datetime import date

from django.contrib import messages
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import View, ListView

from . import __version__ as current_version
from .exceptions import ACPCalendarException
from \
    .forms import CalculatorForm
from .models import ACPHoliday, FiscalYear
from .utils import compare_initial_data_against_db


class HomeView(View):
    template_name = 'acp_calendar/home.html'

    def get(self, request, *args, **kwargs):
        data = self._build_data_dict()
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        if 'update_fiscal_year' in request.POST:
            ACPHoliday.objects.update_fiscal_years()
            data = self._build_data_dict()
        elif 'check_initial_data' in request.POST:
            not_found = compare_initial_data_against_db()
            data = self._build_data_dict()
            data['not_found'] = not_found
        return render(request, self.template_name, data)

    def _build_data_dict(self):
        data = dict()
        data['first_holiday'] = ACPHoliday.objects.first()
        data['last_holiday'] = ACPHoliday.objects.last()
        data['holiday_count'] = ACPHoliday.objects.count()
        data['version'] = current_version
        # OrderNotes.objects.filter(item=item).values_list('shared_note', flat=True).distinct()
        # data['years'] = ACPHoliday.objects.order_by('-fiscal_year').distinct('fiscal_year').values('fiscal_year')
        data['years'] = ACPHoliday.objects.exclude(fiscal_year=0).order_by(
            '-fiscal_year'
        ).values_list('fiscal_year', flat=True).distinct()
        # if len(data['years']) == 1 and data['years'][0] == 0:
        #     data['years'] = []
        return data


class CalendarView(View):
    """
    View to generate a calendar for fiscal year containing the working days in every month
    of the fiscal year.
    """

    template_name = 'acp_calendar/fiscal_year_calendar.html'

    def get(self, request, *args, **kwargs):
        year = int(kwargs['fiscal_year'])
        fiscal_year = FiscalYear(year)
        data = dict()
        data['months'] = list()
        data['version'] = current_version
        data['fiscal_year'] = year
        data['working_days_in_fiscal_year'] = 0
        try:
            for month in fiscal_year.months_in_fiscal_year():
                month_data = dict()
                month_data['month'] = date(month[1], month[0], 1).strftime('%b')
                month_data['year'] = month[1]
                month_data['working_days'] = ACPHoliday.get_working_days_for_month(month[1], month[0])
                data['working_days_in_fiscal_year'] += month_data['working_days']
                data['months'].append(month_data)
            today = timezone.now().date()
            if today <= fiscal_year.end_date:
                data['remaining_working_days_in_fiscal_year'] = ACPHoliday.get_working_days(today, fiscal_year.end_date)
            else:
                data['remaining_working_days_in_fiscal_year'] = 0

            data['remaining_working_days_percentage'] = data['remaining_working_days_in_fiscal_year'] / data[
                'working_days_in_fiscal_year'] * 100
        except ACPCalendarException as e:
            data['errors'] = str(e)
        return render(request, self.template_name, data)


class CalculatorView(View):
    """
    View to calculate the amount of working day between two dates.
    """

    template_name = 'acp_calendar/calculator.html'

    def get(self, request, *args, **kwargs):
        form = CalculatorForm()
        data = {'form': form,
                'version': current_version}
        return render(request, self.template_name, data)

    def post(self, request, *args, **kwargs):
        calculator_form = CalculatorForm(request.POST)
        data = {'form': calculator_form,
                'working_days': None,
                'version': current_version}
        if calculator_form.is_valid():
            start_date = calculator_form.cleaned_data['start_date']
            end_date = calculator_form.cleaned_data['end_date']
            try:
                working_days = ACPHoliday.get_working_days(start_date, end_date)
                data['working_days'] = working_days
                return render(request, self.template_name, data)
            except ACPCalendarException as e:
                messages.add_message(request, messages.ERROR, str(e))
                return render(request, self.template_name, data)
        else:
            return render(request, self.template_name, data)


class ACPHolidayListView(ListView):
    model = ACPHoliday
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(ACPHolidayListView, self).get_context_data(**kwargs)
        if self.kwargs.get('year'):
            context['year'] = self.kwargs.get('year')
        return context

    def get_queryset(self):
        qs = super(ACPHolidayListView, self).get_queryset()
        if self.kwargs.get('year'):
            qs = qs.filter(date__year=int(self.kwargs.get('year')))
        return qs


