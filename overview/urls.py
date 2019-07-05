from django.urls import path

from overview.views import crm

urlpatterns = [
    path('', crm, name='crm_url'),
]