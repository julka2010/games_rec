from django.urls import path

from . import views

app_name = 'training'
urlpatterns = [
    path('everything', views.everything, name='everything'),
    path('player/<int:player_id>', views.player, name='player'),
]
