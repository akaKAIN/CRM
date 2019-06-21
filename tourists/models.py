from django.db import models
from django.urls import reverse
from itertools import chain

class Tourist(models.Model):
    """ Модель описывающая каждого туриста по отдельности  """
    name = models.CharField(max_length=200, verbose_name='ФИО Туриста')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(max_length=50, blank=True, verbose_name='email')
    date_of_arrival = models.DateField(verbose_name='Дата прибытия', blank=True)
    date_of_departure = models.DateField(verbose_name='Дата убытия', blank=True)
    note = models.TextField(max_length=500, verbose_name='Примечание')
    STATUS = (
           ('r', 'заявка сформирована'),
           ('c', 'оплачено'),
           ('d', 'пакет документов готов'),
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
    visa = models.FileField(blank=True, null=True, upload_to='files', verbose_name='Копия визы')
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

    def is_full_package_of_documents(self):
        """ Функция для установки флажка Полный пакет документов, возвращает boolean"""
        if self.visa.name is not None and self.contract.name is not None and self.passport.name is not None:
            return True

    def list_of_business(self):
        """ Функция возвращающая список того, чем и когда занят турист """
        list_of_services = []
        all_business = chain(DatelineForHotel.objects.filter(tourist=self).values_list(
                                                            'hotel__name', 'date_from', 'date_to'),
                             TimelineForNutrition.objects.filter(tourist=self).values_list(
                                                       'nutrition__name', 'time_from', 'time_to'),
                             TimelineForExcursion.objects.filter(tourist=self).values_list(
                                                       'excursion__name', 'time_from', 'time_to')
                             )
        for bis in all_business:
            list_of_services.append(bis)

        return list_of_services


class Group(models.Model):
    """ Модель описывающая группы туристов  """
    name = models.CharField(max_length=200, verbose_name='Название группы')
    manager = models.CharField(max_length=200, verbose_name='Менеджер группы туристов')
    manager_phone = models.CharField(max_length=20)
    STATUS = (
           ('r', 'сформирована'),
           ('e', 'на экскурсии'),
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


class TimelineForNutrition(models.Model):
    """ Пррмежуточная модель для хранения времени начала и окончания питания """
    tourist = models.ForeignKey('Tourist', on_delete=models.CASCADE)
    nutrition = models.ForeignKey('Nutrition', on_delete=models.CASCADE)
    time_from = models.DateTimeField()
    time_to = models.DateTimeField()


class TimelineForExcursion(models.Model):
    """ Пррмежуточная модель для хранения времени начала и окончания экскурсий """
    tourist = models.ForeignKey('Tourist', on_delete=models.CASCADE)
    excursion = models.ForeignKey('Excursion', on_delete=models.CASCADE)
    time_from = models.DateTimeField()
    time_to = models.DateTimeField()


class DatelineForHotel(models.Model):
    """ Пррмежуточная модель для хранения дат заселения и выселения из отеля """
    tourist = models.ForeignKey('Tourist', on_delete=models.CASCADE)
    hotel = models.ForeignKey('Hotel', on_delete=models.CASCADE)
    date_from = models.DateField()
    date_to = models.DateField()

    amount = models.DecimalField(max_digits=11, decimal_places=4, default='100')

class Excursion(models.Model):
    """ Модель описывающая экскурсии, которые посещает турист"""
    name = models.CharField(max_length=300, help_text='Введите название экскурсии')
    note = models.TextField(max_length=500, verbose_name='Описание', blank=True, null=True)
    cost = models.DecimalField(max_digits=7, decimal_places=2)
    timelines = models.ManyToManyField(Tourist, through='TimelineForExcursion')


class Nutrition(models.Model):
    """ Модель описывающая питание туриста """
    name = models.CharField(max_length=300, help_text='Введите название питания')
    note = models.TextField(max_length=500, verbose_name='Описание', blank=True, null=True)
    cost = models.DecimalField(max_digits=7, decimal_places=2)
    timelines = models.ManyToManyField(Tourist, through='TimelineForNutrition')


class Hotel(models.Model):
    """ Модель описывающая отель для туристов  """
    name = models.CharField(max_length=300, help_text='Введите название отеля')
    addres = models.CharField(max_length=300)
    phone = models.CharField(max_length=20)
    cost_for_one_day = models.DecimalField(max_digits=7, decimal_places=2)
    check_in = models.TimeField()
    check_out = models.TimeField()
    datelines = models.ManyToManyField(Tourist, through='DatelineForHotel')
