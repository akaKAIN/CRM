from django.db import models
from django.urls import reverse
import uuid

class Tourist(models.Model):
    """ Модель описывающая каждого туриста по отдельности  """
    name = models.CharField(max_length=200, verbose_name='ФИО Туриста')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(max_length=50, blank=True, verbose_name='email')
    date_of_arrival = models.DateField(verbose_name='Дата прибытия')
    date_of_departure = models.DateField(verbose_name='Дата убытия')
    docs = models.FileField()
    note = models.TextField(max_length=1000, verbose_name='Примечание')
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
        help_text='Статус туриста',
    )
    #list_of_services =
    hotel = models.ForeignKey('Hotel',
                              on_delete=models.SET_NULL,
                              null=True,
                              verbose_name='Отель')
    #number_in_hotel = models.
    group = models.ForeignKey('Group',
                              on_delete=models.SET_NULL,
                              null=True,
                              verbose_name='Группа')
    excursion = models.ManyToManyField('Excursion',
                                       verbose_name='Экскурсии')

    def __str__(self):
        """ Функция, отображающая имя туриста и его телефон"""
        return "{} {}".format(self.name, self.phone)

    def get_absolute_url(self):
        """Возвращает ссылку для получения деталей по туристу"""
        return reverse('tourist-detail', args=[str(self.id)])

    def display_excursion(self):
        """ Функция отображающая все экскурсии на которые записан турист"""
        return ', '.join(excursion.name for excurs in self.excursion.all())


class Files(models.Model):

    file = models.FileField(upload_to='tourist', blank=True, null=True, verbose_name='Файл')
    contact = models.ForeignKey(Tourist, blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Файлы"
        verbose_name_plural = "Файлы"

    def __str__(self):
        return self.file.name


class Hotel(models.Model):
    """ Модель описывающая отель для ттуристов  """
    name = models.CharField(max_length=300, help_text='Введите название отеля')
    addres = models.CharField(max_length=300)
    phone = models.CharField(max_length=20)
    cost_for_one_day = models.DecimalField(max_digits=7, decimal_places=2)
    check_in = models.TimeField()
    check_out = models.TimeField()

class Group(models.Model):
    """ Модель описывающая группы туристов  """
    manager =  models.CharField(max_length=200, help_text='Менеджер группы туристов')
    #manager_phone = models.CharField(max_length=20)
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

class Excursion(models.Model):
    """ Модель описывающая экскурсии на которые записан турист"""
    name = models.CharField(max_length=300, help_text='Введите название экскурсии')
    cost = models.DecimalField(max_digits=7, decimal_places=2)
    time_begin = models.TimeField()
    time_end = models.TimeField()

    def __str__(self):
        """ Функция отображающая название экскурсии"""
        return self.name
