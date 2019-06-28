from django.db import models
from django.urls import reverse
from itertools import chain
from datetime import datetime
from django.db.models import F


class Tourist(models.Model):
    """ Модель, описывающая каждого туриста по отдельности  """
    name = models.CharField(max_length=200, verbose_name='ФИО Туриста')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(max_length=50, blank=True, verbose_name='email')
    date_of_arrival = models.DateField(verbose_name='Дата прибытия', blank=True)
    date_of_departure = models.DateField(verbose_name='Дата убытия', blank=True)
    note = models.TextField(max_length=150, verbose_name='Примечание')
    STATUS = (
           ('r', 'заявка сформирована'),
           ('c', 'оплачено'),
           ('g', 'в группе'),
           ('h', 'заселен в отель'),
           ('e', 'на экскурсии'),
        )

    status = models.CharField(
        max_length=1,
        choices=STATUS,
        blank=True,
        default='r',
        verbose_name='Статус туриста',
    )

    visa = models.FileField(blank=True,
                            null=True,
                            upload_to='files',
                            verbose_name='Копия визы')
    contract = models.FileField(blank=True, null=True, upload_to='files', verbose_name='Копия договора')
    passport = models.FileField(blank=True, null=True, upload_to='files', verbose_name='Копия паспорта')
    others = models.FileField(blank=True, null=True, upload_to='files', verbose_name='Другие документы')

    class Meta:
        ordering = ['date_of_arrival']
        permissions = (("can_edit", "Editing data"),
                       ("can_get_report", "Getting report"), )

    def __str__(self):
        """ Функция, отображающая имя туриста и его телефон"""
        return f"{self.name} {self.phone}"

    def get_absolute_url(self):
        """Возвращает ссылку для получения деталей по туристу"""
        return reverse('tourist-detail', args=[str(self.id)])

    def list_of_business(self):
        """ Функция, возвращающая список того, чем и когда занят турист """

        all_business = chain(DatelineForHotel.objects.filter(tourist=self).values_list(
            'hotel__name', 'date_from', 'date_to', 'hotel__cost_for_one_day', ),
                             TimelineForNutrition.objects.filter(tourist=self).values_list(
            'nutrition__name', 'time_from', 'time_to', 'nutrition__cost'),
                             TimelineForExcursion.objects.filter(tourist=self).values_list(
            'excursion__name', 'time_from', 'time_to', 'excursion__cost')
                             )
        list_of_business = [i for i in all_business]
        return list_of_business

    class Meta:
        verbose_name = 'Турист'
        verbose_name_plural = 'Туристы'


class Group(models.Model):
    """ Модель, описывающая группы туристов  """
    name = models.CharField(max_length=200, verbose_name='Название группы')
    manager = models.CharField(max_length=200, verbose_name='Менеджер группы туристов', blank=True)
    manager_phone = models.CharField(max_length=20, blank=True)
    STATUS = (
           ('f', 'формируется'),
           ('r', 'сформирована'),
           ('e', 'завершена')
        )

    status = models.CharField(
        max_length=1,
        choices=STATUS,
        blank=True,
        default='r',
        help_text='Статус групп туристов',
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class TimelineForNutrition(models.Model):
    """ Промежуточная модель для хранения времени начала и окончания питания """
    time_from = models.DateTimeField(verbose_name='Начало')
    time_to = models.DateTimeField(verbose_name='Окончание')
    tourist = models.ForeignKey('Tourist', on_delete=models.CASCADE, verbose_name = 'Турист')
    nutrition = models.ForeignKey('Nutrition', on_delete=models.CASCADE, 
                                  blank=True, null=True, verbose_name = 'Питание')
    group = models.ForeignKey('Group', on_delete=models.SET_NULL, 
                              blank=True, null=True, verbose_name = 'Группа')

    class Meta:
        get_latest_by = "date_from"
        verbose_name_plural = "Время для питания"

        
class TimelineForExcursion(models.Model):
    """ Промежуточная модель для хранения времени начала и окончания экскурсий """
    time_from = models.DateTimeField(verbose_name='начало экскурсии')
    time_to = models.DateTimeField(verbose_name='окончание экскурсии')
    tourist = models.ForeignKey('Tourist', on_delete=models.CASCADE)
    excursion = models.ForeignKey('Excursion', on_delete=models.SET_NULL,
                                  blank=True, null=True, verbose_name = 'Экскурсии')
    group = models.ForeignKey('Group', on_delete=models.CASCADE, 
                              blank=True, null=True, verbose_name = 'Группа')

    class Meta:
        get_latest_by = "date_from"
        verbose_name_plural = "Время для экскурсий"

class DatelineForHotel(models.Model):
    """ Промежуточная модель для хранения дат заселения и выселения из отеля """
    tourist = models.ForeignKey('Tourist', on_delete=models.CASCADE)
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    date_from = models.DateField(blank=True, verbose_name='Дата заселения')
    date_to = models.DateField(blank=True, verbose_name='Дата выселения')

    def _get_number_of_days(self):
        """ Возвращает количество дней между заселением в отель и выселением """
        num = (self.date_to - self.date_from).days
        # Если заселение-выселение в один день, платить все равно за одни сутки
        if num < 1:
            num = 1
        return num

    number_of_days = property(_get_number_of_days)

    class Meta:
        get_latest_by = "date_from"
        verbose_name_plural = "Временная ось для пребывания в отелях"


class Excursion(models.Model):
    """ Модель описывающая экскурсии, которые посещает турист"""
    name = models.CharField(max_length=300, help_text='Введите название экскурсии')
    note = models.TextField(max_length=500, verbose_name='Описание', blank=True, null=True)
    cost = models.DecimalField(max_digits=7, decimal_places=2)
    timelines = models.ManyToManyField(Tourist, through='TimelineForExcursion')

    def __str__(self):
        """ Функция, отображающая название экскурсии """
        return self.name

    class Meta:
        verbose_name = 'Экскурсия'
        verbose_name_plural = 'Экскурсии'


class Nutrition(models.Model):
    """ Модель описывающая питание туриста """
    name = models.CharField(max_length=300, help_text='Введите название питания')
    note = models.TextField(max_length=500, verbose_name='Описание', blank=True, null=True)
    cost = models.DecimalField(max_digits=7, decimal_places=2)
    timelines = models.ManyToManyField(Tourist, through='TimelineForNutrition')

    def __str__(self):
        """ Функция, отображающая наименование питания """
        return self.name

    class Meta:
        verbose_name = 'Питание'
        verbose_name_plural = 'Питание'

class Hotel(models.Model):
    """ Модель описывающая отель для туристов  """
    name = models.CharField(max_length=300, verbose_name='Название отеля', help_text='Введите название отеля')
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
