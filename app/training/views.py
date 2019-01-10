from celery.decorators import task
from django.http import HttpResponse
from django.shortcuts import render

from ratings.models import Player
from training.tasks import (
    train_everything,
    train_player,
)

def everything(request):
    train_everything.delay()
    return HttpResponse('Training has started')

def player(request, username):
    player = Player.objects.get(bgg_username=username)
    train_player.delay(player)
    return HttpResponse('Training has started')
