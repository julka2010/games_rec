from celery.result import AsyncResult
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404, render

from ratings.forms import PlayerSearchForm
from ratings.models import Player
from training.models import KerasSinglePlayerModel

def index(request):
    if request.method == 'POST':
        form = PlayerSearchForm(request.POST)
        if form.is_valid():
            player = get_object_or_404(
                Player,
                bgg_username=form.cleaned_data['search_query']
            )
            return HttpResponseRedirect('/training/player/{}'.format(player.id))
    else:
        form = PlayerSearchForm()
    return render(request, 'recommendations/index.html', {'form': form})

def recommendations(request, player_id=None, model_id=None, task_id=None):
    ended = AsyncResult(task_id).ready()
    if not ended:
        return HttpResponse(
            "Recommendations are not ready yet.\n"
            "Please check in about 30 secs."
        )
    if model_id:
        model = get_object_or_404(KerasSinglePlayerModel, pk=model_id)
    elif player_id:
        model = get_list_or_404(KerasSinglePlayerModel, player_id=player_id)[-1]
    else:
        raise RuntimeError(
            'Personal recommendations should always get model_id or player_id')
    recommendations = model.get_recommendations()
    context = {'recommendations' : recommendations}
    return render(request, 'recommendations/recommendation_list.html', context)
