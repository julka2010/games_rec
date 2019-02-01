from django.contrib.postgres.fields import JSONField
from django.db import models
from django_pandas.managers import DataFrameManager

class Game(models.Model):
    bgg_id = models.IntegerField(
        default=None, blank=True, null=True,
        unique=True,
    )
    objects = DataFrameManager()
    title = models.CharField(max_length=255)
    min_players = models.IntegerField(default=None, blank=True, null=True)
    max_players = models.IntegerField(default=None, blank=True, null=True)
    min_playtime = models.IntegerField(default=None, blank=True, null=True)
    max_playtime = models.IntegerField(default=None, blank=True, null=True)
    weight = models.FloatField(default=None, blank=True, null=True)
    dump = JSONField(default=dict)


class Player(models.Model):
    bgg_username = models.CharField(
        max_length=255,
        default=None, blank=True, null=True
    )
    objects = DataFrameManager()
    games = models.ManyToManyField(Game, through='rating')

    @property
    def unplayed_games(self):
        """Returns queryset of games player haven't played yet."""
        played_games = self.games.values('pk')
        return Game.objects.exclude(pk__in=played_games)


class Rating(models.Model):
    player = models.ForeignKey(Player, models.CASCADE)
    game = models.ForeignKey(Game, models.CASCADE)
    value = models.FloatField(default=8.7)
    objects = DataFrameManager()
    class Meta:
        unique_together = (('player', 'game'))
