from django.urls import include, path
from rest_framework import routers
from front import views

app_name = 'front'

urlpatterns = [
    path('first_join', views.FirstJoinView.as_view(), name="first_join"),
    path('second_join', views.SecondJoinView.as_view(), name="second_join"),
    path('live/start', views.LiveStartView.as_view(), name="live_start"),
    path('api/token', views.GetTokenView.as_view(), name='get_token'),
    
    path('staff', views.StaffView.as_view(), name='staff'),
    path('api/get_room_participants/', views.GetRoomParticipantsView.as_view(), name='get_room_participants'),
    path('api/remove_participant/', views.RemoveParticipantView.as_view(), name='remove_participant'),
    path('api/toggle_track/', views.ToggleTrackView.as_view(), name='toggle_track'),
]

