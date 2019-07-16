from django.db import models
from itertools import chain
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.utils import timezone
from overview.make_gantt import *


class Group(models.Model):
    """ Модель, описывающая группы туристов """
    group_name = models.CharField(verbose_name='Название группы',
                                  max_length=50
                                  )
    date_of_arrival = models.DateField(verbose_name='Дата прибытия группы',
                                       null=True, blank=True
                                       )
    date_of_departure = models.DateField(verbose_name='Дата убытия группы',
                                         null=True, blank=True
                                         )
    STATUS = (
           ('f', 'группа формируется'),
           ('c', 'группа прибыла'),
           ('g', 'группа уехала'),
        )

    status = models.CharField(verbose_name='Статус группы',
        max_length=1,
        choices=STATUS,
        blank=True,
        default='f'
    )

    def __str__(self):
        return f' Группа {self.group_name}'

    def clean(self):
        if not self.date_of_arrival or not self.date_of_departure:
            raise ValidationError("Заполните пустые поля")
        if self.date_of_arrival > self.date_of_departure:
            raise ValidationError(
                'Дата убытия не может быть раньше даты прибытия')

    class Meta:
        verbose_name = "Группу" 
        verbose_name_plural = "Группы" 
        ordering = ['date_of_arrival']


class Tourist(models.Model):
    """ Модель, описывающая каждого туриста по отдельности  """
    name = models.CharField(verbose_name='ФИО Туриста',
        max_length=200
        )
    phone = models.CharField(verbose_name='Телефон',
        max_length=20)
    email = models.EmailField(verbose_name='email',
        max_length=50,
        blank=True, null=True
        )
    note = models.TextField(verbose_name='Примечание',
        max_length=100,
        blank=True, null=True
        )
    visa = models.FileField(verbose_name='Копия визы',
        blank=True, null=True,
        upload_to='files'
        )
    insurance = models.FileField(verbose_name='Копия страховки',
        blank=True, null=True,
        upload_to='files'
        )
    passport = models.FileField(verbose_name='Копия паспорта',
        blank=True, null=True,
        upload_to='files'
        )
    group = models.ForeignKey('Group', verbose_name='Группа',
        on_delete=models.SET_NULL,
        blank=True, null=True
    )
    is_paid = models.BooleanField(verbose_name='оплачено',
        default=False
    )

    class Meta:
        verbose_name = 'Туриста'
        verbose_name_plural = "Туристы" 

    @property
    def status(self):
        ''' Функция для установки вычисляемого поля статус '''
        from datetime import datetime 

        is_await = Tourist.objects.filter(id=self.id, 
                group__date_of_arrival__gte=timezone.now()
                )
        is_left = Tourist.objects.filter(id=self.id, 
                group__date_of_departure__lte=timezone.now()
                )
        is_nutr = TimelineForNutrition.objects.filter(tourist=self.id, 
            time_from__lte=timezone.now(), 
            time_to__gte=timezone.now()
            )
        on_excur = TimelineForExcursion.objects.filter(tourist=self.id, 
            time_from__lte=timezone.now(),
            time_to__gte=timezone.now() 
            )
        in_hotel = DatelineForHotel.objects.filter(tourist=self.id, 
            time_from__lte=timezone.now(),
            time_to__gte=timezone.now()
            )

        if is_await:
            _status = 'ожидается приезд'
        elif is_left:
            _status = 'уехал'
        elif not in_hotel:
            _status = 'не заселен в гостиницу'
        elif not is_nutr or not on_excur:
            _status = 'ничем не занят'
        else:
            _status = ' - '

        return _status 


    def gantt_to_html(self) -> str:
        """ Функция берет список всех занятий туриста и рисует по ним диаграммы
        возвращает строковое представление HTML странички с диаграммами """
        all_business = chain(
            # DatelineForHotel.objects.filter(tourist=self).values_list(
            #     'hotel__name', 'time_from', 'time_to'),
            TimelineForNutrition.objects.filter(tourist=self).values_list(
                'nutrition__name', 'time_from', 'time_to'),
            TimelineForExcursion.objects.filter(tourist=self).values_list(
                'excursion__name', 'time_from', 'time_to')
        )
        list_of_business = [i for i in all_business]
        return start_gantt(list_of_business)
  
    def check_doc(self):
        doc_pack = Tourist.objects.filter(
            id=self.id
        ).values('visa', 'insurance', 'passport')
        for pack in doc_pack:
            for _, doc in pack.items():
                if doc is None or doc == '':
                    return False
        return True
        
    def check_hotel(self):
        return set(DatelineForHotel.objects.filter(
            tourist=self.id
        ).values_list('hotel__name', flat=True))

    def check_nutrition(self):
        return set(TimelineForNutrition.objects.filter(
            tourist=self.id
        ).values_list('nutrition__name', flat=True))
  

    def __str__(self):
        """ Функция, отображающая имя туриста и его телефон"""
        return f'{self.name} {self.phone}'


class FeedFile(models.Model):
    file = models.FileField(blank=True, null=True, upload_to="files/%Y/%m/%d")
    feed = models.ForeignKey(Tourist, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Другие документы'
        verbose_name_plural = 'Другие документы'


class Event(models.Model):
    """ Модель, описывающая события, в которых могут участвовать туристы  """
    name = models.CharField(max_length=200, verbose_name='Название события')
    manager = models.CharField(verbose_name='Менеджер группы туристов',
        max_length=200,
        blank=True
        )

    manager_phone = models.CharField(verbose_name='Телефон менеджера',
        max_length=20, 
        blank=True,
        )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'


class Timeline(models.Model):
    ''' Абстрактная модель для временных осей '''
    time_from = models.DateTimeField(verbose_name='Начало')
    time_to = models.DateTimeField(verbose_name='Окончание')
    tourist = models.ForeignKey('Tourist', verbose_name='Турист',
        on_delete=models.CASCADE
        )
    event = models.ForeignKey('Event', verbose_name='Событие',
        on_delete=models.CASCADE,
        blank=True, null=True
        )

    class Meta:
        abstract = True       
        get_latest_by = "date_from" 

    def clean(self):
        if not self.time_from or not self.time_to:
            raise ValidationError("Заполните пустые поля")
        
        if self.time_from > self.time_to: 
            raise ValidationError(
               'Время начала не может быть больше времени окончания')

        # Проверим, нет ли у этого туриста других дел на это время

        tle = TimelineForExcursion.objects.filter(Q(tourist=self.tourist),
            Q(time_from__gt=self.time_from, time_from__lt=self.time_to) |
            Q(time_to__gt=self.time_from, time_to__lt=self.time_to)
            ).exclude(id=self.id)

        tln = TimelineForNutrition.objects.filter(Q(tourist=self.tourist),
            Q(time_from__gt=self.time_from, time_from__lt=self.time_to) |
            Q(time_to__gt=self.time_from, time_to__lt=self.time_to)
            ).exclude(id=self.id)
        # Если хотя бы один запрос вернулся не пустым
        if tle or tln:
            raise ValidationError('Выберите другое время, это уже занято') 


class TimelineForNutrition(Timeline):
    """ Промежуточная модель для хранения времени начала и окончания питания """
    
    nutrition = models.ForeignKey('Nutrition', verbose_name='Питание',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
        )

    class Meta:
        verbose_name_plural = "Время для питания"

       
class TimelineForExcursion(Timeline):
    """ Промежуточная модель для хранения времени начала и окончания экскурсий """
    excursion = models.ForeignKey('Excursion', verbose_name='Экскурсии',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
        )

    class Meta:
        verbose_name_plural = "Время для экскурсий"
 

class DatelineForHotel(Timeline):
    """ Промежуточная модель для хранения дат заселения и выселения из отеля """
    hotel = models.ForeignKey('Hotel', verbose_name='Отели', 
        on_delete=models.SET_NULL,
        blank=True,
        null=True
        )

    class Meta:
        verbose_name_plural = "Пребывание в отелях"

    def clean(self):
        if not self.time_from or not self.time_to:
            raise ValidationError("Заполните пустые поля")
        
        if self.time_from > self.time_to: 
            raise ValidationError(
               'Время заселения не может быть меньше времени выселения')

        # Проверим, не живет ли турист в другой гостинице это время

        dlh = DatelineForHotel.objects.filter(Q(tourist=self.tourist),
            Q(time_from__gt=self.time_from, time_from__lt=self.time_to) |
            Q(time_to__gt=self.time_from, time_to__lt=self.time_to)
            ).exclude(id=self.id)

        # Если запрос вернулся не пустым
        if dlh:
            raise ValidationError(f'Выберите другое время, это уже занято')     


class Excursion(models.Model):
    """ Модель описывающая экскурсии, которые посещает турист"""
    name = models.CharField(verbose_name='Название экскурсии',
        max_length=300
        )
    note = models.TextField(verbose_name='Описание',
        max_length=500,
        blank=True, null=True
        )
    cost = models.DecimalField(verbose_name='Стоимость',
        max_digits=7, 
        decimal_places=2
        )
    timelines = models.ManyToManyField(Tourist,
        through='TimelineForExcursion'
        )

    def __str__(self):
        """ Функция, отображающая название экскурсии """
        return self.name

    class Meta:
        verbose_name = 'Экскурсия'
        verbose_name_plural = 'Экскурсии'


class Nutrition(models.Model):
    """ Модель описывающая питание туриста """
    name = models.CharField(verbose_name='Наименование',
        max_length=300
        )
    note = models.TextField(verbose_name='Описание',
        max_length=500,
        blank=True, null=True
        )
    cost = models.DecimalField(verbose_name='Стоимость',
        max_digits=7, 
        decimal_places=2
        )
    timelines = models.ManyToManyField(Tourist,
        through='TimelineForNutrition'
        )

    def __str__(self):
        """ Функция, отображающая наименование питания """
        return self.name

    class Meta:
        verbose_name = 'Питание'
        verbose_name_plural = 'Питание'


class Hotel(models.Model):
    """ Модель описывающая отель для туристов  """
    name = models.CharField(verbose_name='Название отеля',
        max_length=300
        )
    addres = models.CharField(verbose_name='Адрес отеля',
        max_length=300
        )
    phone = models.CharField(verbose_name='Телефон отеля',
        max_length=20
        )
    cost_for_one_day = models.DecimalField(verbose_name='Стоимость за сутки',
        max_digits=7, 
        decimal_places=2
        )
    check_in = models.TimeField(verbose_name='Время заселения')
    check_out = models.TimeField(verbose_name='Время выезда')
    datelines = models.ManyToManyField(Tourist, through='DatelineForHotel')

    def __str__(self):
        """ Функция, отображающая название отеля """
        return self.name

    class Meta:
        verbose_name = 'Отель'
        verbose_name_plural = 'Отели'
