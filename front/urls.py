from django.urls import include, path
from rest_framework import routers
from front import views

app_name = 'front'

urlpatterns = [
    path('test', views.TestView.as_view(), name="test"),
    path('join', views.JoinView.as_view(), name="join"),
    path('live/start', views.LiveStartView.as_view(), name="live_start"),
    path('api/token', views.GetTokenView.as_view(), name='get_token'),
]

