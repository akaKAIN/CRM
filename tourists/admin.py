from django.contrib import admin
from tourists.models import Tourist, Nutrition, Hotel, Group, Excursion


class TouristAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name',)
    filter_horizontal = ('excursion',)


class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'addres', 'phone')
    list_filter = ('cost_for_one_day',)
    ordering = ('-cost_for_one_day',)


admin.site.register(Tourist, TouristAdmin)
admin.site.register(Nutrition)
admin.site.register(Hotel, HotelAdmin)
admin.site.register(Group)
admin.site.register(Excursion)


