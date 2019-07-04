from django.shortcuts import render
from tourists.models import Tourist, Group


# Create your views here.
def crm(request):
    groups = Group.objects.values('group_name')

    tourists = Tourist.objects.first()
    gantt = tourists.gantt_to_html()

    context = {
        'groups': groups,
        'tourists': tourists,
        'gantt': gantt,

    }
    return render(request, 'crm.html', context=context)
