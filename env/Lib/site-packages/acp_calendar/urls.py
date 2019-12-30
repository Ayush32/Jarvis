from django.conf.urls import url, include

from .views import CalculatorView, CalendarView, HomeView, ACPHolidayListView

urlpatterns = [
    url(r'^list/$', ACPHolidayListView.as_view(), name='list'),
    url(r'^list/(?P<year>\d{4})/$', ACPHolidayListView.as_view(), name='list-year'),
    url(r'^calculator/', CalculatorView.as_view(), name='calculator'),
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^fiscal-year-calendar/(?P<fiscal_year>\d{4})', CalendarView.as_view(), name='fiscal-year-calendar'),
    url(r'^api/', include('acp_calendar.api.urls', namespace='calendar-api')),
]
