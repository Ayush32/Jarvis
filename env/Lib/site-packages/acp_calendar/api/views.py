from rest_framework import views
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from .serializers import ACPHolidaySerializer, StandardResultsSetPagination
from ..models import ACPHoliday, ACPCalendarException


class ACPHolidayListAPIView(ListAPIView):
    # queryset = ACPHoliday.objects.all()
    serializer_class = ACPHolidaySerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        year = self.kwargs.get('year', None)
        if year:
            return ACPHoliday.objects.filter(date__year=int(year))
        else:
            return ACPHoliday.objects.all()


class CalendarCalculationsView(views.APIView):
    def get(self, request, **kwargs):

        calculation = kwargs.pop('calculation', None)
        data = None
        if calculation == 'working_days':
            data = self.working_days(**kwargs)
        elif calculation == 'working_delta':
            data = self.working_delta(**kwargs)
        elif calculation == 'working_month':
            data = self.working_days_in_month(**kwargs)
        else:
            raise ACPCalendarException('Invalid Calculation')

        return Response(data)

    def working_days(self, start_date, end_date):
        results = {'start_date': start_date,
                   'end_date': end_date,
                   'days': '-1',
                   }
        try:
            days = ACPHoliday.get_working_days(start_date, end_date)
            results['days'] = str(days)
        except ACPCalendarException as e:
            results['error'] = str(e)

        return results

    def working_delta(self, start_date, days):
        results = {'start_date': start_date,
                   'end_date': None,
                   'days': days,
                   }
        try:
            end_date = ACPHoliday.working_delta(start_date, days)
            results['end_date'] = end_date
        except ACPCalendarException as e:
            results['error'] = str(e)

        return results

    def working_days_in_month(self, year, month):
        results = {'year': year,
                   'month': month,
                   'days': '-1',
                   }
        try:
            results['days'] = str(ACPHoliday.get_working_days_for_month(int(year), int(month)))
        except ACPCalendarException as e:
            results['error'] = str(e)
        return results
