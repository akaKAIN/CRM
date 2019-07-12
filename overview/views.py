from django.shortcuts import render
from tourists.models import Tourist, Group
from django.views.generic import TemplateView


class CRM(TemplateView):
    template_name = 'overview/crm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        groups_with_tourists = {}
        groups = Group.objects.exclude(status='g')
        for group in groups:
            groups_with_tourists.update({group: Tourist.objects.filter(group=group.id).order_by('name')})

        context.update(
            {'groups': groups_with_tourists}
        )
        return context
