from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from ratings.forms import PlayerSearchForm
from ratings.models import Player

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

def recommendations(request, player_id=None, model_id=None):
    return HttpResponse("You are checking recommendations for you.")
