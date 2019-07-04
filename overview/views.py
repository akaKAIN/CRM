from django.shortcuts import render
from tourists.models import Tourist, Group


# Create your views here.
def crm(request):
    groups = Group.objects.first
    tourists = Tourist.objects.all()
    context = {
        'groups': groups,
        'tourists': tourists,
    }
    return render(request, 'crm.html', context=context)
