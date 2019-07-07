from django.shortcuts import render
from tourists.models import Tourist, Group


# Create your views here.
def crm(request):
    groups_with_tourists = {}
    groups = Group.objects.filter(status='r')
    for group in groups:
        groups_with_tourists.update({group.group_name: Tourist.objects.filter(group=group.id)})
    context = {'groups': groups_with_tourists}
    return render(request, 'crm.html', context=context)
