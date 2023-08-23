from django.db import models

# Create your models here.
class BotServer(models.Model):
    server_id = models.CharField(max_length=100)
    owner_id = models.CharField(max_length=100)
    templates = models.JSONField(default=dict)
    member_count = models.IntegerField(default=0)

    class Meta:
        db_table = 'bot_server'