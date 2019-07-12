from django.contrib import admin
from datetime import datetime, timedelta
from django.urls import reverse
from django.conf.urls import url
from django.utils.html import format_html

from tourists.models import (TimelineForNutrition, DatelineForHotel, Files,
TimelineForExcursion, Tourist, Event, Group, Hotel, Excursion, Nutrition)
from tourists import views


class DatelineForHotelInline(admin.TabularInline):
    model = DatelineForHotel
    extra = 1
    fields = ('hotel', ('time_from', 'time_to'))


class TimelineForNutritionInline(admin.TabularInline):
    model = TimelineForNutrition
    extra = 1
    fields = ('nutrition', ('time_from', 'time_to'), 'event')
    readonly_fields = ['event']
    show_change_link = True
    
    # то что уже съедено вчера и позже нам не интересно  
    def get_queryset(self, request):
        query_set = super(TimelineForNutritionInline, self
            ).get_queryset(request)
        return query_set.filter(
            time_from__gte=datetime.now() - timedelta(days=1))


class TimelineForExcursionInline(admin.TabularInline):
    model = TimelineForExcursion
    extra = 1
    fields = ('excursion', ('time_from', 'time_to'), 'event')
    readonly_fields = ['event']
    show_change_link = True


class FilesInline(admin.StackedInline):
    model = Files
    extra = 1
    fields = ('visa', 'passport', 'insurance', 'others')


class TouristAdmin(admin.ModelAdmin):
    list_display = (
        'colored_name', 
        'phone',
        'is_full_package_of_documents', 
        'is_paid',
        'status',
        'tourist_actions', 
        'note'
        )
    
    search_fields = ('name',)
    filter_horizontal = ('excursion',)

    inlines = [
        FilesInline,
        TimelineForNutritionInline,
        TimelineForExcursionInline,
        DatelineForHotelInline,
        ]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<pk>.+)/list_of_services/$',
                self.admin_site.admin_view(views.show_list_services),
                name='show-list-services'),
            #url(
            #    r'^(?P<pk>.+)/gantt_chart/$',
            #    self.admin_site.admin_view(views.gantt_chart),
            #    name='gant-chart',
            #),
        ]
        return custom_urls + urls

    def tourist_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Список услуг</a>&nbsp;',
            #'<a class="button" href="{}">Диаграмма Ганта</a>',
            reverse('admin:show-list-services', args=[obj.pk])#,
            #reverse('admin:gant-chart', args=[obj.pk]),
        )
    tourist_actions.short_description = 'Кнопки'
    tourist_actions.allow_tags = True 


    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if isinstance(instance, TimelineForNutrition):
                # перед сохранением ищем подходящую группу, в которой турист 
                # может питаться 
                tl_nutr = TimelineForNutrition.objects.filter(
                    time_from=instance.time_from).exclude(
                    id=instance.id).first()
                # если никто в это время не питается и запрос вернулся пустой
                # cоздаём новое событие для Питания
                if not tl_nutr:
                    new_event = Event.objects.create(name=
                        f"Питание в {instance.time_from}")
                    instance.event = new_event
                else:
                    instance.event = tl_nutr.event 
                instance.save()
            elif isinstance(instance, TimelineForExcursion):
                # ищем подходящую по времени и названию экскурсию
                tl_ex = TimelineForExcursion.objects.filter(
                    time_from=instance.time_from).filter(
                    excursion__name=instance.excursion).exclude(
                    id=instance.id).first()
                # если никто в это время на эту экскурсию не идёт и запрос 
                # вернулся пустой, создаём новое событие для Экскурсии
                if not tl_ex:
                    new_event = Event.objects.create(name=
                      f"Экскурсия {instance.excursion} в {instance.time_from}")
                    instance.event = new_event
                else:
                    instance.event = tl_ex.event
                instance.save()
            else:
                instance.save()  
        formset.save_m2m()


    def is_full_package_of_documents(self, obj):
        """ Функция для установки флажка Полный пакет документов"""
        have_all_docs = Files.objects.filter(tourist=obj.id).exclude(visa=''
                                                           ).exclude(insurance=''
                                                           ).exclude(passport='')
        if have_all_docs:
            return True
        else:
            return False    

    is_full_package_of_documents.boolean = True
    is_full_package_of_documents.short_description = "Полный пакет документов"

    def colored_name(self, obj):
        if obj.status == 'ожидается приезд':   color = 'ff9900'
        elif obj.status == 'уехал': color = '66ff33'
        elif obj.status == 'ничем не занят': color = '000000'
        elif obj.status == 'не заселен в гостиницу': color = 'ff0000'
        else:    
            color = 'grey'
        return format_html('<b><span style="color: #{};">{}</span><b>',
                           color, obj.name)

    colored_name.short_description = 'ФИО Туриста'
    colored_name.allow_tags = True


class TouristInline(admin.TabularInline):
    model = Tourist
    extra = 3
    fields = ('name', 'phone', 'email', 'note', )


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'group_name', 'status', 'date_of_arrival', 'date_of_departure'
        )
    search_fields = ('name',)
    date_hierarchy = 'date_of_arrival'
    list_filter = ('status', )

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
    model = TimelineForNutrition
    extra = 0
    fields = ('nutrition', 'time_from', 'time_to', 'tourist')
    can_delete = False
    readonly_fields = ('nutrition', 'time_from', 'time_to', 'tourist')

class TimelineForExcursionEventInline(admin.TabularInline):
    model = TimelineForExcursion
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


admin.site.register(Tourist, TouristAdmin)
admin.site.register(Nutrition, NutritionAdmin)
admin.site.register(Hotel)
admin.site.register(Excursion, ExcursionAdmin)
admin.site.register(Event, EventAdmin)
admin.site.register(Group, GroupAdmin)