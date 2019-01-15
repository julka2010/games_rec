"""Url patterns for recommendations app."""
from django.urls import path

from . import views

app_name = 'recommendations'
urlpatterns = [
    path('', views.index, name='index'),
    path('<int:player_id>', views.recommendations, name='player-recommendations'),
    path('anon/<int:model_id>', views.recommendations, name='anon-recommendations'),
]
