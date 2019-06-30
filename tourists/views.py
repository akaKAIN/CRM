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


def show_list_services(request, pk):
    tourist = Tourist.objects.get(id=pk)
    total = 0
    # просуммируем все услуги
    for i in tourist.list_of_business():
        total = total + i[3]
    context = {
        'list_of_services': tourist.list_of_business(),
        'total': total
        }
    # Передаём HTML шаблону index.html данные контекста
    return render(request, 'tourists/show_list_services.html', context=context)