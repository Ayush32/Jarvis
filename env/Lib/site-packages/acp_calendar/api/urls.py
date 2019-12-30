from django.conf.urls import url

from . import views

urlpatterns = [
    url(r"^working-days/(?P<start_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<end_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/$",
        views.CalendarCalculationsView.as_view(), {'calculation': 'working_days'}, name="working_days", ),
    url(r"^working-delta/(?P<start_date>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<days>[0-9]+)/$",
        views.CalendarCalculationsView.as_view(), {'calculation': 'working_delta'}, name="working_delta"),
    url(r"^working-month/(?P<year>[0-9]{4})/(?P<month>[0-9]{1,2})/$",
        views.CalendarCalculationsView.as_view(), {'calculation': 'working_month'}, name="working_month"),
    url(r'^holiday-list/$', views.ACPHolidayListAPIView.as_view(), name='holiday-list'),
    url(r'^holiday-list/(?P<year>[0-9]{4})/$', views.ACPHolidayListAPIView.as_view(), name='holiday-list-year'),
]
