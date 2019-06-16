from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('tourists/', views.TouristListView.as_view(), name='tourists'),
    path('tourist/new', views.CreateTouristView.as_view(), name='create-tourist'),
    path('tourist/<int:pk>', views.TouristDetailView.as_view(), name='tourist-detail'),
    path('tourist/<int:pk>/update', views.UpdateTouristView.as_view(), name='update-tourist'),
    path('tourist/<int:pk>/delete', views.DeleteTouristView.as_view(), name='delete-tourist'),
    path('groups/', views.GroupListView.as_view(), name='groups'),
    path('excurs/', views.ExcurListView.as_view(), name='excurs'),
    path('hotels/', views.HotelListView.as_view(), name='hotels'),
]
