from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.index, name='index'),
    path('tourists/', views.TouristListView.as_view(), name='tourists'),
    path('tourist/<int:pk>', views.TouristDetailView.as_view(), name='tourist-detail'),
    path('tourist/<int:pk>/edit/$', views.EditTourist, name='edit-tourist'),
	path('groups/', views.GroupListView.as_view(), name='groups'),
    path('excurs/', views.ExcurListView.as_view(), name='excurs'),
    path('hotels/', views.HotelListView.as_view(), name='hotels'),
]
