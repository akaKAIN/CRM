from django.shortcuts import render
from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render_to_response
from qsstats import QuerySetStats
from django.db.models import Count

from .models import Tourist, Hotel, Group, Excursion, DatelineForHotel
from .forms import TouristModelForm


def gantt_chart(request):
    start_date = DatelineForHotel.objects.order_by('date_from').values_list(
                                                'date_from', flat=True).first()
    end_date = DatelineForHotel.objects.order_by('date_to').values_list(
                                                'date_to', flat=True).last()

    queryset = DatelineForHotel.objects.all()

    # считаем количество платежей...
    qsstats = QuerySetStats(queryset, date_field='date_from', aggregate=Count('id'))
    # ...в день за указанный период
    values = qsstats.time_series(start_date, end_date, interval='days')

    return render_to_response('gantt_chart.html', {'values': values})


def index(request):
    """Вью главной страницы"""

    # Вычисляем общее количество туристов
    num_tourists = Tourist.objects.all().count()

    # Количество туристов, готовых к приёму (с готовыми документами)
    num_tour_ready = Tourist.objects.filter(status__exact='d').count()

    # Количество туристов, распределенных в группы
    num_tour_in_group = Tourist.objects.filter(status__exact='g').count()

    # Количество сформированных групп
    num_group = Group.objects.all().count()

    # Количество доступных экскурсий
    num_excurs = Excursion.objects.all().count()

    # Количество отелей
    num_hotel = Hotel.objects.all().count()

    context = {
        'num_tourists': num_tourists,
        'num_tour_ready': num_tour_ready,
        'num_tour_in_group': num_tour_in_group,
        'num_group': num_group,
        'num_excurs': num_excurs,
        'num_hotel': num_hotel
        }

    # Передаём HTML шаблону index.html данные контекста
    return render(request, 'index.html', context=context)


class TouristListView(generic.ListView):
    model = Tourist
    paginate_by = 10
    context_object_name = 'tourist_list'
    queryset = Tourist.objects.all()
    template_name = 'tourists/tourist_list.html'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            # тут неплохо бы сделать поиск по нескольким полям, по имени и телефону например
            return Tourist.objects.filter(name__icontains=query)
        else:
            return Tourist.objects.all()


class CreateTouristView(generic.edit.CreateView):
    model = Tourist
    template_name_suffix = '_create_form'
    success_url = '/tourists/'
    form_class = TouristModelForm


class UpdateTouristView(generic.edit.UpdateView):
    model = Tourist
    template_name_suffix = '_update_form'
    success_url = '/tourists/'
    form_class = TouristModelForm


class DeleteTouristView(generic.edit.DeleteView):
    model = Tourist
    fields = '__all__'
    template_name_suffix = '_delete_form'
    success_url = '/tourists/'


def tourist_detail(request, pk):
    tourist = Tourist.objects.get(id=pk)
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

    # Передаём HTML шаблону index.html данные контекста
    return render(request, 'tourists/tourist_detail.html', context=context)




class GroupListView(generic.ListView):
    model = Group
    paginate_by = 10
    context_object_name = 'group_list'
    queryset = Group.objects.all()[:5]
    template_name = 'groups/group_list.html'


class ExcurListView(generic.ListView):
    model = Excursion
    paginate_by = 10
    context_object_name = 'excur_list'
    queryset = Excursion.objects.all()[:5]
    template_name = 'excurs/excur_list.html'


class HotelListView(generic.ListView):
    model = Hotel
    paginate_by = 10
    context_object_name = 'hotel_list'
    queryset = Hotel.objects.all()[:5]
    template_name = 'hotels/hotel_list.html'
