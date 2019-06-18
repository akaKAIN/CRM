from django.db import models
from django.urls import reverse


class Tourist(models.Model):
    """ Модель описывающая каждого туриста по отдельности  """
    name = models.CharField(max_length=200, verbose_name='ФИО Туриста')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(max_length=50, blank=True, verbose_name='email')
    date_of_arrival = models.DateField(verbose_name='Дата прибытия')
    date_of_departure = models.DateField(verbose_name='Дата убытия')
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
    nutrition = models.ManyToManyField('Nutrition',
                                       verbose_name='Питание')
    hotel = models.ManyToManyField('Hotel',
                                   verbose_name='Отель')
    group = models.ForeignKey('Group',
                              on_delete=models.SET_NULL,
                              null=True,
                              verbose_name='Группа')
    excursion = models.ManyToManyField('Excursion',
                                       verbose_name='Экскурсии')

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

    def display_excursion(self):
        """ Функция отображающая все экскурсии на которые записан турист"""
        return ', '.join(excurs.name for excurs in self.excursion.all())

    def is_full_package_of_documents(self):
        """ Функция для установки флажка Полный пакет документов, возвращает boolean"""
        return self.visa.name and self.contract.name and self.passport.name


class Nutrition(models.Model):
    """ Модель описывающая питание туриста """
    name = models.CharField(max_length=300, verbose_name='Питание')
    cost = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        return self.name


class Hotel(models.Model):
    """ Модель описывающая отель для туристов  """
    name = models.CharField(max_length=300, help_text='Введите название отеля')
    addres = models.CharField(max_length=300)
    phone = models.CharField(max_length=20)
    cost_for_one_day = models.DecimalField(max_digits=7, decimal_places=2)
    check_in = models.TimeField()
    check_out = models.TimeField()

    def __str__(self):
        return self.name


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


class Excursion(models.Model):
    """ Модель описывающая экскурсии на которые записан турист"""
    name = models.CharField(max_length=300, help_text='Введите название экскурсии')
    note = models.TextField(max_length=500, verbose_name='Описание', blank=True, null=True)
    cost = models.DecimalField(max_digits=7, decimal_places=2)

    def __str__(self):
        """ Функция отображающая название экскурсии"""
        return self.name
