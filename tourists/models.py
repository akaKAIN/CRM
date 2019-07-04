from django.db import models
from django.urls import reverse

from itertools import chain
from overview.make_gantt import *


class Group(models.Model):
    """ Модель, описывающая группы туристов """
    group_name = models.CharField(max_length=50,
                                  verbose_name='Название группы'
                                  )
    date_of_arrival = models.DateField(verbose_name='Дата прибытия группы',
                                       null=True,
                                       blank=True
                                       )
    date_of_departure = models.DateField(verbose_name='Дата убытия группы',
                                         null=True, blank=True
                                         )
    STATUS = (
           ('r', 'заявка сформирована'),
           ('c', 'группа прибыла'),
           ('g', 'группа уехала'),
        )

    status = models.CharField(
        max_length=1,
        choices=STATUS,
        blank=True,
        default='r',
        verbose_name='Статус группы',
    )

    def __str__(self):
        return f' Группа {self.group_name}'

    class Meta:
        verbose_name_plural = "Группы" 
        ordering = ['date_of_arrival']


class Tourist(models.Model):
    """ Модель, описывающая каждого туриста по отдельности  """
    name = models.CharField(max_length=200, verbose_name='ФИО Туриста')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(
        max_length=50,
        blank=True,
        verbose_name='email'
    )
    note = models.TextField(
        max_length=100,
        verbose_name='Примечание',
        blank=True, null=True
    )
    visa = models.FileField(
        blank=True,
        null=True,
        upload_to='files',
        verbose_name='Копия визы'
    )
    insurance = models.FileField(
        blank=True, null=True,
        upload_to='files',
        verbose_name='Копия страховки'
    )
    passport = models.FileField(
        blank=True,
        null=True,
        upload_to='files',
        verbose_name='Копия паспорта'
    )
    others = models.FileField(
        blank=True, null=True,
        upload_to='files',
        verbose_name='Другие документы'
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        blank=True, null=True,
        verbose_name = 'Группа'
    )

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

    def __str__(self):
        """ Функция, отображающая имя туриста и его телефон"""
        return f'{self.name} {self.phone}'

    class Meta:
        verbose_name_plural = "Туристы" 
        permissions = (("can_edit", "Editing data"),
                       ("can_get_report", "Getting report"), )   


class Event(models.Model):
    """ Модель, описывающая события, в которых могут участвовать туристы  """
    name = models.CharField(max_length=200, verbose_name='Название события')
    manager = models.CharField(
        max_length=200,
        verbose_name='Менеджер группы туристов',
        blank=True
    )
    manager_phone = models.CharField(max_length=20, blank=True)
    STATUS = (
           ('p', 'планируется'),
           ('c', 'длится'),
           ('e', 'закончилось')
        )

    status = models.CharField(
        max_length=1,
        choices=STATUS,
        blank=True,
        default='p',
        help_text='Статус события',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Событие'
        verbose_name_plural = 'События'


class TimelineForNutrition(models.Model):
    """ Промежуточная модель для хранения времени начала и окончания питания """
    time_from = models.DateTimeField(verbose_name='Начало')
    time_to = models.DateTimeField(verbose_name='Окончание')

    tourist = models.ForeignKey(
        'Tourist',
        on_delete=models.CASCADE,
        verbose_name = 'Турист'
    )
    nutrition = models.ForeignKey(
        'Nutrition',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name = 'Питание'
    )
    event = models.ForeignKey(
        'Event',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Событие'
    )

    class Meta:
        get_latest_by = "date_from"
        verbose_name_plural = "Время для питания"

        
class TimelineForExcursion(models.Model):
    """ Промежуточная модель для хранения времени начала и окончания экскурсий """
    time_from = models.DateTimeField(verbose_name='начало экскурсии')
    time_to = models.DateTimeField(verbose_name='окончание экскурсии')
    tourist = models.ForeignKey(
        'Tourist',
        on_delete=models.CASCADE,
        verbose_name='Турист'
    )
    excursion = models.ForeignKey(
        'Excursion',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Экскурсии'
    )
    event = models.ForeignKey(
        'Event',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name='Событие'
    )

    class Meta:
        get_latest_by = "date_from"
        verbose_name_plural = "Время для экскурсий"


class DatelineForHotel(models.Model):
    """ Промежуточная модель для хранения дат заселения и выселения из отеля """
    tourist = models.ForeignKey('Tourist', on_delete=models.CASCADE)
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    time_from = models.DateField(blank=True, verbose_name='Дата заселения')
    time_to = models.DateField(blank=True, verbose_name='Дата выселения')

    class Meta:
        get_latest_by = "time_from"
        verbose_name_plural = "Временная ось для пребывания в отелях"


class Excursion(models.Model):
    """ Модель описывающая экскурсии, которые посещает турист"""
    name = models.CharField(
        max_length=300,
        help_text='Введите название экскурсии'
    )
    note = models.TextField(
        max_length=500,
        verbose_name='Описание',
        blank=True, null=True
    )
    cost = models.DecimalField(max_digits=7, decimal_places=2)
    timelines = models.ManyToManyField(Tourist,
                                       through='TimelineForExcursion')

    def __str__(self):
        """ Функция, отображающая название экскурсии """
        return self.name

    class Meta:
        verbose_name = 'Экскурсия'
        verbose_name_plural = 'Экскурсии'


class Nutrition(models.Model):
    """ Модель описывающая питание туриста """
    name = models.CharField(
        max_length=300,
        help_text='Введите название питания'
    )
    note = models.TextField(
        max_length=500,
        verbose_name='Описание',
        blank=True, null=True
    )
    cost = models.DecimalField(max_digits=7, decimal_places=2)
    timelines = models.ManyToManyField(Tourist,
                                       through='TimelineForNutrition')

    def __str__(self):
        """ Функция, отображающая наименование питания """
        return self.name

    class Meta:
        verbose_name = 'Питание'
        verbose_name_plural = 'Питание'

class Hotel(models.Model):
    """ Модель описывающая отель для туристов  """
    name = models.CharField(
        max_length=300,
        verbose_name='Название отеля',
        help_text='Введите название отеля'
    )
    addres = models.CharField(max_length=300)
    phone = models.CharField(max_length=20)
    cost_for_one_day = models.DecimalField(max_digits=7, decimal_places=2)
    check_in = models.TimeField()
    check_out = models.TimeField()
    datelines = models.ManyToManyField(Tourist, through='DatelineForHotel')

    def __str__(self):
        """ Функция, отображающая название отеля """
        return self.name

    class Meta:
        verbose_name = 'Отель'
        verbose_name_plural = 'Отели'
