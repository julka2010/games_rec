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
from training.tasks import train_player
from .tasks import get_player_recommendations

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
            task_id = chain(
                train_player.s(player.id),
                get_player_recommendations.s()
            ).apply_async().id
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
    if not task_id:
        task_id = get_player_recommendations.delay(player_id).id
        url = build_url(
            'recommendations:player-recommendations',
            kwargs={
                'player_id': player_id,
                'get': {'task_id': task_id},
            }
        )
        return HttpResponseRedirect(url)

    res = AsyncResult(task_id)
    if not res.ready():
        return HttpResponse(
            "Recommendations are not ready yet.\n"
            "Please check in about 30 secs."
        )

    recs = pd.read_json(res.result)
    titles = Game.objects.get_by_pks(recs.pk).to_dataframe(['bgg_id', 'title'])
    context = {'recommendation_list' : titles}
    return render(request, 'recommendations/recommendation_list.html', context)
