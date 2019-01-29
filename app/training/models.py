from django.db import models
from keras.models import load_model
from lazy import lazy
import pandas as pd

from training.keras.metrics import acceptable_absolute_deviation
from ratings.models import Game, Player

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
    keras_model_file = models.FileField(
        editable=False,
        upload_to='keras_models',
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

    @lazy
    def keras_model(self):
        return load_model(
            self.keras_model_file.path,
            custom_objects={
                'acceptable_absolute_deviation': acceptable_absolute_deviation,
            }
        )

    def get_recommendations(self, games_id, limit=100):
        from training.keras.data_preparation import (
            to_board_game_geek_ids,
            to_keras_model_indices,
        )
        to_be_pred = pd.DataFrame(games_id, columns=['game_id'])
        to_be_pred['player_id'] = self.player_id
        to_be_pred = to_keras_model_indices(to_be_pred)
        ratings, _ = self.keras_model.predict( # pylint: disable=no-member
            {
                'user_in': to_be_pred.player_id.values,
                'item_in': to_be_pred.game_id.values,
            },
        )
        recommendations = pd.DataFrame({
            'prediction': ratings.reshape(-1),
            'model_game_id': to_be_pred.game_id.values
        }).sort_values('prediction', ascending=False).reset_index(drop=True)
        return to_board_game_geek_ids(recommendations.iloc[:limit])
