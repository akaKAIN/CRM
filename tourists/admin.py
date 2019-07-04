from django.contrib import admin
from datetime import datetime
from django.utils import timezone 
from django.urls import path

from tourists import models


class DatelineForHotelInline(admin.TabularInline):
    model = models.DatelineForHotel
    extra = 1


class TimelineForNutritionInline(admin.TabularInline):
    model = models.TimelineForNutrition
    extra = 1
    fields = ('nutrition', ('time_from', 'time_to'), 'event')
    readonly_fields = ['event']
    show_change_link = True
    print(model._meta.fields)
    
    # то что уже съедено в прошлом нам не интересно  
    def get_queryset(self, request):
        query_set = super(TimelineForNutritionInline, self
            ).get_queryset(request)
        return query_set.filter(time_from__gte=datetime.now(tz=timezone.utc))


class TimelineForExcursionInline(admin.TabularInline):
    model = models.TimelineForExcursion
    extra = 1
    fields = ('excursion', ('time_from', 'time_to'),'event')
    readonly_fields = ['event']
    show_change_link = True


class TouristAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'is_full_package_of_documents', 'phone'
        )
    search_fields = ('name',)
    filter_horizontal = ('excursion',)
    inlines = [
        TimelineForNutritionInline,
        TimelineForExcursionInline,
        DatelineForHotelInline,
    ]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if instance.__class__.__name__== 'TimelineForNutrition':
                # перед сохранением ищем подходящую группу, в которой турист может питаться
                # получаем список времени начала питаний всех туристов в будущем
                tl_nutr_infuture = models.TimelineForNutrition.objects.filter(
                    time_from__gte=datetime.now(tz=timezone.utc)).exclude(
                    id=instance.id)
                # если подходящей группы нет, создаём её и присваиваем имя        
                if instance.time_from not in tl_nutr_infuture.values_list('time_from', flat=True):
                    new_event_name = f"Питание в {instance.time_from}"
                    new_event = models.Event.objects.create(name=new_event_name, 
                                                            status='p')
                else:
                    for j in [i for i in tl_nutr_infuture]:
                        if instance.time_from == j.time_from:
                            new_event = j.event 
                            print(new_event)
                instance.event = new_event    
                instance.save()
            elif instance.__class__.__name__== 'TimelineForExcursion':
                # ищем подходящую по времени и названию экскурсию
                tl_ex_infuture = models.TimelineForExcursion.objects.filter(
                    time_from__gte=datetime.now(tz=timezone.utc)).filter(
                    excursion__name=instance.excursion).exclude(id=instance.id)
                # если подходящей группы нет, создаём её и присваиваем имя
                # и статус "формируется"        
                if instance.time_from not in tl_ex_infuture.values_list('time_from', flat=True):
                    new_event_name = f"Экскурсия {instance.excursion} в {instance.time_from}"
                    new_event = models.Event.objects.create(name=new_event_name, 
                                                            status='p')
                else:
                    for j in [i for i in tl_ex_infuture]:
                        if instance.time_from == j.time_from:
                            new_event = j.event 
                            print(new_event)
                instance.event = new_event    
                instance.save()
            else:
                instance.save()    
        formset.save_m2m()

    def is_full_package_of_documents(self, obj):
        """ Функция для установки флажка Полный пакет документов"""
        visa = models.Tourist.objects.get(id = obj.id).visa
        have_visa = visa is not None and visa.name != ''
        insurance = models.Tourist.objects.get(id = obj.id).insurance
        have_insurance = insurance is not None and insurance.name != ''
        passport = models.Tourist.objects.get(id = obj.id).passport
        have_passport = passport is not None and passport.name != ''
        return have_visa and have_insurance and have_passport

    is_full_package_of_documents.boolean = True


class TouristInline(admin.TabularInline):
    model = models.Tourist
    extra = 3
    fields = ('name', 'phone', 'email', 'note', )


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'date_of_arrival', 'date_of_departure'
        )
    search_fields = ('name',)
    date_hierarchy = 'date_of_arrival'

    inlines = [
        TouristInline,
    ]


class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'addres', 'phone')
    list_filter = ('cost_for_one_day',)
    ordering = ('-cost_for_one_day',)
    list_filter =('name',)


class NutritionAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost')
    ordering = ('cost',)


class ExcursionAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost')
    ordering = ('cost',)


class TimelineForNutritionEventInline(admin.TabularInline):
    model = models.TimelineForNutrition
    extra = 0
    fields = ('nutrition', 'time_from', 'time_to', 'tourist')
    can_delete = False
    readonly_fields = ('nutrition', 'time_from', 'time_to', 'tourist')

class TimelineForExcursionEventInline(admin.TabularInline):
    model = models.TimelineForExcursion
    extra = 0
    fields = ('excursion', 'time_from', 'time_to', 'tourist')
    can_delete = False
    readonly_fields = ('excursion', 'time_from', 'time_to', 'tourist')


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'manager_phone')
    inlines = [
        TimelineForNutritionEventInline,
        TimelineForExcursionEventInline,
    ]


admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Tourist, TouristAdmin)
admin.site.register(models.Nutrition, NutritionAdmin)
admin.site.register(models.Hotel, HotelAdmin)
admin.site.register(models.Excursion, ExcursionAdmin)
admin.site.register(models.Event, EventAdmin)