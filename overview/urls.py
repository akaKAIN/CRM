from django.urls import path

from overview.views import CRM

urlpatterns = [
    path('', CRM.as_view(), name='crm_url'),
]