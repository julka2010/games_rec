from celery import  shared_task

from training.models import KerasSinglePlayerModel
from training.tasks import get_player_predictions
from ratings.models import Player

@shared_task
def get_player_recommendations(player_id, games_id=None, limit=100):
    if games_id is None:
        player = Player.objects.get(pk=player_id)
        games_id = list(player.unplayed_games.standalone_games(
            ).filter(ratings_count__gte=100
            ).to_dataframe('id').reset_index(drop=True).id)
    model = KerasSinglePlayerModel.objects.filter(player_id=player_id).last()

    return get_player_predictions(model.id, games_id, limit)
