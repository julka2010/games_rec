import logging

from celery import chain
from celery.result import AsyncResult
from django.http import QueryDict, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.urls import reverse
import pandas as pd

from ratings.forms import PlayerSearchForm
from ratings.models import Game, Player
from training.models import KerasSinglePlayerModel
from training.tasks import train_player, get_player_predictions

def build_url(viewname, kwargs):
    """django.urls.reverse + request.get parameters.

    Taken from https://stackoverflow.com/a/20459192
    """
    params = kwargs.pop('get', {})
    url = reverse(viewname, kwargs=kwargs)
    if not params:
        return url

    qdict = QueryDict('', mutable=True)
    for k, v in params.items():
        if isinstance(v, list):
            qdict.setlist(k, v)
        else:
            qdict[k] = v

    return url + '?' + qdict.urlencode()


def index(request):
    if request.method == 'POST':
        form = PlayerSearchForm(request.POST)
        if form.is_valid():
            player = get_object_or_404(
                Player,
                bgg_username=form.cleaned_data['search_query']
            )
            task_id = train_player.delay(player.id).id
            url = build_url(
                'recommendations:player-recommendations',
                kwargs={
                    'player_id': player.id,
                    'get': {'task_id': task_id},
                }
            )
            return HttpResponseRedirect(url)
    else:
        form = PlayerSearchForm()
    return render(request, 'recommendations/index.html', {'form': form})


def recommendations(request, player_id=None):
    task_id = request.GET.get('task_id', None)
    ended = AsyncResult(task_id).ready() if task_id else True
    if not ended:
        return HttpResponse(
            "Recommendations are not ready yet.\n"
            "Please check in about 30 secs."
        )
    if player_id:
        model = get_list_or_404(KerasSinglePlayerModel, player_id=player_id)[-1]
    else:
        raise RuntimeError(
            'Personal recommendations should always get model_id or player_id')
    player = Player.objects.get(pk=player_id)
    unplayed_games = player.unplayed_games.standalone_games(
        ).filter(ratings_count__gte=100
        ).to_dataframe('id').reset_index(drop=True).id
    recs = model.get_recommendations(unplayed_games)
    titles = Game.objects.get_by_pks(recs.pk).to_dataframe(['bgg_id', 'title'])
    logging.error(titles)
    context = {'recommendation_list' : titles}
    return render(request, 'recommendations/recommendation_list.html', context)
