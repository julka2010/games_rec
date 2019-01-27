from django.db import models
import pandas as pd

from ratings.models import Game, Player
from training.keras.data_preparation import (
    to_board_game_geek_ids,
    to_keras_model_indices,
)

class TrainedOnGame(models.Model):
    id_in_model = models.PositiveIntegerField(
        editable=False,
        primary_key=True
    )
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

class TrainedOnPlayer(models.Model):
    id_in_model = models.PositiveIntegerField(
        editable=False,
        primary_key=True
    )
    player = models.ForeignKey(Player, on_delete=models.CASCADE)

class KerasSinglePlayerModel(models.Model):
    epoch = models.IntegerField()
    keras_model = models.FileField(
        editable=False,
        upload_to='keras_models'
    )
    loss = models.FloatField()
    output_mean_absolute_error = models.FloatField(null=True, default=None)
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE,
        editable=False,
        null=True, blank=True, default=None,
    )
    val_loss = models.FloatField()
    val_output_mean_absolute_error = models.FloatField(null=True, default=None)

    def get_recommendations(self, games_id, limit=100):
        to_be_pred = pd.DataFrame(games_id)
        to_be_pred['player_id'] = self.player_id
        to_be_pred = to_keras_model_indices(to_be_pred)
        ratings, _ = self.keras_model.predict(
            {
                'user_in': to_be_pred.player_id.values,
                'item_in': to_be_pred.game_id.values,
            },
        )
        recommendations = pd.DataFrame(
            {'prediction': ratings, 'model_game_id': to_be_pred.game_id.values}
        ).sort_values('prediction').reset_index(drop=True)
        return to_board_game_geek_ids(recommendations.iloc[:limit])
