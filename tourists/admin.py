from django.contrib import admin
from datetime import datetime
from django.utils import timezone 
from django.urls import path

from tourists import models


class DatelineForHotelInline(admin.TabularInline):
    model = models.DatelineForHotel
    extra = 1


class TimelineForNutrition(admin.ModelAdmin):
    model = models.TimelineForNutrition
    fields = ('nutrition', ('time_from', 'time_to'), 'tourist')


class TimelineForNutritionInline(admin.TabularInline):
    model = models.TimelineForNutrition
    extra = 1
    fields = ('nutrition', ('time_from', 'time_to'), 'group')
    readonly_fields = ['group']
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
    fields = ('excursion', ('time_from', 'time_to'),'group')
    readonly_fields = ['group']
    show_change_link = True


class TimelineForNutritionAdmin(admin.ModelAdmin):
    list_display = ('time_from', 'time_to', 'tourist', 'group')
    readonly_fields = ['group']


class DatelineForHotelAdmin(admin.ModelAdmin):
    list_display = ('date_from', 'date_to', 'tourist', 'number_of_days')


class TouristAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'is_full_package_of_documents', 'phone', 'date_of_arrival'
        )
    search_fields = ('name',)
    filter_horizontal = ('excursion',)
    date_hierarchy = 'date_of_arrival'
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
                if instance.time_from not in [i.time_from for i in tl_nutr_infuture]:
                    new_group_name = f"Питание в {instance.time_from}"
                    new_group = models.Group.objects.create(name=new_group_name, 
                                                            status='f')
                else:
                    for j in [i for i in tl_nutr_infuture]:
                        if instance.time_from == j.time_from:
                            new_group = j.group 
                            print(new_group)
                instance.group = new_group    
                instance.save()
            elif instance.__class__.__name__== 'TimelineForExcursion':
                # ищем подходящую по времени и названию экскурсию
                tl_ex_infuture = models.TimelineForExcursion.objects.filter(
                    time_from__gte=datetime.now(tz=timezone.utc)).filter(
                    excursion__name=instance.excursion).exclude(id=instance.id)
                # если подходящей группы нет, создаём её и присваиваем имя
                # и статус "формируется"        
                if instance.time_from not in [i.time_from for i in tl_ex_infuture]:
                    new_group_name = f"Экскурсия {instance.excursion} в {instance.time_from}"
                    new_group = models.Group.objects.create(name=new_group_name, 
                                                            status='f')
                else:
                    for j in [i for i in tl_ex_infuture]:
                        if instance.time_from == j.time_from:
                            new_group = j.group 
                            print(new_group)
                instance.group = new_group    
                instance.save()
        formset.save_m2m()

    def is_full_package_of_documents(self, obj):
        """ Функция для установки флажка Полный пакет документов"""
        visa = models.Tourist.objects.get(id = obj.id).visa
        have_visa = visa is not None and visa.name != ''
        contract = models.Tourist.objects.get(id = obj.id).contract
        have_contract = contract is not None and contract.name != ''
        passport = models.Tourist.objects.get(id = obj.id).passport
        have_passport = passport is not None and passport.name != ''
        return have_visa and have_contract and have_contract

    is_full_package_of_documents.boolean = True

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('my_view/', self.my_view),
        ]
        return my_urls + urls

    def my_view(self, request):
        tourist = models.Tourist.objects.get(id=pk)
        total = 0
        # просуммируем все услуги
        for i in tourist.list_of_business():
            total = total + i[3]
        context = {
            'name': tourist.name,
            'phone': tourist.phone,
            'email': tourist.email,
            'date_of_arrival': tourist.date_of_arrival,
            'date_of_departure': tourist.date_of_departure,
            'note': tourist.note,
            'status': tourist.status,
            'list_of_services': tourist.list_of_business(),
            'total': total
            }
        return TemplateResponse(request, 'tourists/tourist_detail.html', context)

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


class TimelineForNutritionGroupInline(admin.TabularInline):
    model = models.TimelineForNutrition
    extra = 0
    fields = ('nutrition', 'time_from', 'time_to', 'tourist')
    can_delete = False
    readonly_fields = ('nutrition', 'time_from', 'time_to', 'tourist')

class TimelineForExcursionGroupInline(admin.TabularInline):
    model = models.TimelineForExcursion
    extra = 0
    fields = ('excursion', 'time_from', 'time_to', 'tourist')
    can_delete = False
    readonly_fields = ('excursion', 'time_from', 'time_to', 'tourist')


class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'manager', 'manager_phone')
    #if 
    inlines = [
        TimelineForNutritionGroupInline,
        TimelineForExcursionGroupInline,
    ]


admin.site.register(models.Tourist, TouristAdmin)
admin.site.register(models.Nutrition, NutritionAdmin)
admin.site.register(models.Hotel, HotelAdmin)
admin.site.register(models.Excursion)
admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.TimelineForNutrition, TimelineForNutritionAdmin)
admin.site.register(models.TimelineForExcursion)
admin.site.register(models.DatelineForHotel, DatelineForHotelAdmin)
