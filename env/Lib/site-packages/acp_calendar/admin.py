from django.contrib import admin

from .models import HolidayType, ACPHoliday


class HolidayTypeAdmin(admin.ModelAdmin):
    list_display = ('short_name', 'name')


class ACPHolidayAdmin(admin.ModelAdmin):
    list_display = ('date', 'holiday_type', 'fiscal_year')


admin.site.register(HolidayType, HolidayTypeAdmin)
admin.site.register(ACPHoliday, ACPHolidayAdmin)
