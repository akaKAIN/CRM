from django.contrib import admin
from django.urls import path, re_path, include
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url
from django.views.static import serve


from tourists import views

urlpatterns = [
    path('crm/', include('overview.urls')),
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/admin/'), name='home'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# ... the rest of your URLconf goes here ...

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {
            'document_root': settings.MEDIA_ROOT,
        }),
    ]

admin.site.site_header = "CRM Туристическая фирма"
admin.site.site_title = "CRM Туристическая фирма"