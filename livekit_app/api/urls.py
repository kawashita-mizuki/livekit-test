from django.urls import include, path
from rest_framework import routers
from api import views

app_name = 'api'

urlpatterns = [
    path('room/list', views.RoomListView.as_view()),
    path('token/create', views.TokenCreateView.as_view()),
    path('room/create', views.RoomCreateView.as_view()),
]

