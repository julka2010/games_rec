from django.test import TestCase

from ratings.models import Player
from training.models import KerasSinglePlayerModel
from training.tasks import train_player

PEDRATOR = Player.objects.get(bgg_username='Pedrator')

class SinglePlayerModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # just so correct worker gets the task
        train_player.delay(PEDRATOR.id).wait(interval=1)
        cls.model = KerasSinglePlayerModel.objects.last()
        cls.ratings = PEDRATOR.ratings_set.to_dataframe(
            ['game_id', 'player_id', 'value']
        ).sort_values('value', ascending=True).reset_index(drop=True)

    def compare_higher_test(self):
        higher = self.ratings.iloc[-10:]
        lower = self.ratings.iloc[:10]
        for h, l in zip(higher.value, lower.value):
            assert h > l, "Incorrect data fed."
            highest, values = model.keras_model.predict(inputs)
            self.assertGreater(highest[0], highest[1])
