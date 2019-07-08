from django.shortcuts import render
from tourists.models import Tourist, Group


# Create your views here.
def re_dict() -> dict:
    new_dict = {}
    mans = Tourist.objects.all()
    for man in mans:
        new_dict.update({man.id: man.gantt_to_html()})

    return new_dict


def crm(request):

    context = {
        'groups': Group.objects.filter(status='f').values(),
        'tourists': Tourist.objects.all(),


    }
    return render(request, 'crm.html', context=context)
