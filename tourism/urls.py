from django.contrib import admin
from django.urls import include
from django.urls import path
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from django.views.generic import TemplateView

from django.contrib.auth.decorators import user_passes_test

from tourists import views

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('tourists/', include('tourists.urls')),
    #path('', RedirectView.as_view(url='/tourists/')),
    path('', RedirectView.as_view(url='/admin/')),
    path('list_of_services/<int:pk>', views.show_list_services,
        	name='show_list_services'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Add Django site authentication urls (for login, logout, password management)
urlpatterns += [
    url(r'^accounts/', include('django.contrib.auth.urls')),
]
