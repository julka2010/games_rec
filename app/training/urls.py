from django.urls import include, path

from . import views

urlpatterns = [
    # TODO admin protect this (or functionaly same) url
    path('everything', views.everything, name='everything'),
    path('/player/<username>/', views.player, name='train_for_player'),
]
