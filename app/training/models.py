from django.db import models

from ratings.models import Game, Player

class TrainedOnGame(models.Model):
    id_in_model = models.PositiveIntegerField(primary_key=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

class TrainedOnPlayer(models.Model):
    id_in_model = models.PositiveIntegerField(primary_key=True)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
