# weather_stations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('metar/ping', views.ping_response, name="ping"),
    path('metar/info', views.weather_response, name="station_weather"),

    #path('chat/<str:username>/', views.chatPage, name='chat'),
    #path('', views.index, name='index'),
    #path('<str:room_name>/', views.room, name='room'),
]
