from django.urls import re_path

from overview.views import crm

urlpatterns = [
    re_path(r'', crm, name='crm_url'),
]