from django.shortcuts import render
from django.views.generic.edit import FormView
from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import Tourist, Hotel, Group, Excursion, Files
from .forms import EditTouristModelForm

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

class TouristView(FormView):
    form_class = EditTouristModelForm
    template_name = 'tourist.html'
    success_url = 'success_url.html'

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('files')
        if form.is_valid():
            id = form.save().pk
            tourist = Tourist.objects.get(pk=id)
            if files:
                for f in files:
                    fl = Files(tourist=tourist, file = f)
                    fl.save()
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

class TouristListView(generic.ListView):
    model = Tourist
    paginate_by = 2
    context_object_name = 'tourist_list'   # your own name for the list as a template variable
    queryset = Tourist.objects.all()[:5] # Get 5 books containing the title war
    template_name = 'tourists/tourist_list.html'  # Specify your own template name/location

class TouristDetailView(generic.DetailView):
    model = Tourist

class GroupListView(generic.ListView):
    model = Group
    paginate_by = 2
    context_object_name = 'group_list'   # your own name for the list as a template variable
    queryset = Group.objects.all()[:5] # Get 5 books containing the title war
    template_name = 'groups/group_list.html'  # Specify your own template name/location

class ExcurListView(generic.ListView):
    model = Excursion
    paginate_by = 2
    context_object_name = 'excur_list'   # your own name for the list as a template variable
    queryset = Excursion.objects.all()[:5] # Get 5 books containing the title war
    template_name = 'excurs/excur_list.html'  # Specify your own template name/location

class HotelListView(generic.ListView):
    model = Hotel
    paginate_by = 2
    context_object_name = 'hotel_list'   # your own name for the list as a template variable
    queryset = Hotel.objects.all()[:5] # Get 5 books containing the title war
    template_name = 'hotels/hotel_list.html'  # Specify your own template name/location

def EditTourist(request, pk):
    """
    Функция для редактирования туриста
    """
    tourist_inst=get_object_or_404(Tourist, pk = pk)

    # Если это POST запрос, обработаем данные формы
    if request.method == 'POST':

        # Создадим экземпляр формы и свяжем его с данными из запроса
        form = EditTouristModelForm(request.POST)

        # Если форма правильная
        if form.is_valid():
            tourist_inst.name = form.cleaned_data['name']
            tourist_inst.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('tourist-detail') )

    # Если GET это или какой другой запрос, создаем форму по умолчанию
    else:
        form = EditTouristModelForm(initial={'new_name': 'Новое имя',})

    return render(request, 'tourists/tourist_edit.html', {'form': form, 'touristinst':tourist_inst})
