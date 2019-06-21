from django.contrib import admin
from tourists.models import Tourist, Nutrition, Hotel, Group, Excursion


class TouristAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'date_of_arrival')
    search_fields = ('name',)
    filter_horizontal = ('excursion',)


class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'addres', 'phone')
    list_filter = ('cost_for_one_day',)
    ordering = ('-cost_for_one_day',)


class NutritionAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost')
    ordering = ('cost',)


admin.site.register(Tourist, TouristAdmin)
admin.site.register(Nutrition, NutritionAdmin)
admin.site.register(Hotel, HotelAdmin)
admin.site.register(Group)
admin.site.register(Excursion)


