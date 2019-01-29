from django.http import HttpResponse
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from ratings.models import Player
from training.tasks import (
    train_everything,
    train_player,
)

def everything(request):
    train_everything.delay()
    return HttpResponse('Training has started')

def player(request, player_id):
    task = train_player.delay(player_id)
    response = redirect(
        "/recommendations/{player_id}?task_id={task_id}".format(
            player_id=player_id,
            task_id=task.id,
        )
    )
    return response
