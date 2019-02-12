from django.db import models


class Game(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField()
    updated_date = models.DateField()
    updated_time = models.TimeField()
    active = models.BooleanField()
    max_score = models.BigIntegerField()


class Player(models.Model):
    nickname = models.CharField(max_length=100)
    score = models.BigIntegerField()
    last_login_at = models.DateTimeField()

    game = models.ForeignKey(Game, on_delete=models.CASCADE)


class Action(models.Model):
    ACTION_FIRE = 'fire'
    ACTION_MOVE = 'move'
    ACTION_STOP = 'stop'

    ACTIONS = (
        (ACTION_FIRE, 'Fire'),
        (ACTION_MOVE, 'Move'),
        (ACTION_STOP, 'Stop'),
    )

    name = models.CharField(max_length=4, choices=ACTIONS)
    executed_at = models.DateTimeField()

    actor = models.ForeignKey(Player, related_name='actions', null=True, on_delete=models.CASCADE)
    target = models.ForeignKey(Player, related_name='enemy_actions+', null=True, on_delete=models.CASCADE)
