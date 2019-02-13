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
    player = models.ForeignKey(
        Player, on_delete=models.CASCADE,
        editable=False,
        null=True, blank=True, default=None,
    )
    val_loss = models.FloatField()

    @lazy
    def keras_model(self):
        return load_model(
            self.keras_model_file.path,
            custom_objects={
                'acceptable_absolute_deviation': acceptable_absolute_deviation,
            }
        )
