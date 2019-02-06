from celery import shared_task

from ratings.models import Game

@shared_task
def recompute_ratings_count():
    games = Game.objects.all()
    for game in games:
        game.ratings_count = game.rating_set.count()
        game.save()
