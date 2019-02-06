from django.contrib.postgres.fields import JSONField
from django.db import models
from django_pandas.managers import (
    DataFrameManager,
    DataFrameQuerySet,
)


class GamesQuerySet(DataFrameQuerySet):
    def standalone_games(self):
        return self.filter(standalone=True)

    def get_by_pks(self, pks):
        """Returns qs finding by pks and preserving given pks order.

        Soitje's code taken from
        https://stackoverflow.com/a/37648265/4371768
        """
        preserved = models.Case(
            *[models.When(pk=pk, then=pos) for pos, pk in enumerate(pks)])
        return self.filter(pk__in=pks).order_by(preserved)

    def by_ratings_count(self, **kwds):
        """Adds annotation 'ratings_count' and filters immediately.

        It is expected to use ratings_count__gte and ratings_count__lte
        here, mostly.
        """
        return self.annotate(ratings_count=models.Count('rating')
            ).filter(**kwds)


# pylint: disable=invalid-name
GamesManager = models.Manager.from_queryset(GamesQuerySet)
# pylint: enable=invalid-name


class Game(models.Model):
    objects = GamesManager()

    bgg_id = models.IntegerField(
        default=None, blank=True, null=True,
        unique=True,
    )
    dump = JSONField(default=dict)
    max_players = models.IntegerField(default=None, blank=True, null=True)
    max_playtime = models.IntegerField(default=None, blank=True, null=True)
    min_players = models.IntegerField(default=None, blank=True, null=True)
    min_playtime = models.IntegerField(default=None, blank=True, null=True)
    ratings_count = models.IntegerField(default=0, editable=False)
    standalone = models.BooleanField(default=True)
    title = models.CharField(max_length=255)
    weight = models.FloatField(default=None, blank=True, null=True)


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
