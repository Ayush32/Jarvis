from rest_framework import serializers
from rest_framework.pagination import PageNumberPagination

from ..models import HolidayType, ACPHoliday


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 1000


class HolidayTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayType
        fields = ('id', 'name')


class ACPHolidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = ACPHoliday
        fields = ('id', 'date', 'holiday_type')
