from django.shortcuts import render
from tourists.models import Tourist, Group


# Create your views here.
def crm(request):
    groups_with_tourists = {}
    groups = Group.objects.exclude(status='g')
    for group in groups:
        groups_with_tourists.update({group: Tourist.objects.filter(group=group.id).order_by('name')})
    context = {'groups': groups_with_tourists}
    return render(request, 'crm.html', context=context)
