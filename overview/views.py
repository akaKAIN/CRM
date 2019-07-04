from django.shortcuts import render
from tourists.models import DatelineForHotel, TimelineForNutrition, TimelineForExcursion, Tourist, Group
from itertools import chain
from overview.make_gantt import *


class Gantt(Tourist):

    def gantt_to_html(self) -> str:
        """ Функция берет список всех занятий туриста и рисует по ним диаграммы
        возвращает строковое представление HTML странички с диаграммами """
        all_business = chain(
            DatelineForHotel.objects.filter(tourist=self).values_list(
                'hotel__name', 'date_from', 'date_to'),
            TimelineForNutrition.objects.filter(tourist=self).values_list(
                'nutrition__name', 'time_from', 'time_to'),
            TimelineForExcursion.objects.filter(tourist=self).values_list(
                'excursion__name', 'time_from', 'time_to')
        )
        list_of_business = [i for i in all_business]
        return start_gantt(list_of_business)


# Create your views here.
def crm(request):
    groups = Group.objects.all()
    tourist = Tourist.objects.first()
    gantt = Gantt.objects.all()
    context = {
        'groups': groups,
        'tourist': tourist,
        'gatts': gantt
    }
    return render(request, 'crm.html', context=context)
