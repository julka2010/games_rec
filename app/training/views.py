from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render

from ratings.models import Player
from training.tasks import (
    train_everything,
    train_player,
)

def everything(request):
    train_everything.delay()
    return HttpResponse('Training has started')

def player(request, player_id):
    train_player.delay(player_id)
    return HttpResponse('Training has started')
