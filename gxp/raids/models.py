import uuid
from django.db import models

from gxp.raiders.models import Raider

class Raid(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.IntegerField()
    zone = models.CharField(max_length=255, blank=True, default='')
    warcraftLogsId = models.CharField(max_length=255, blank=True, default='')
    optional = models.BooleanField(default=True)
    raiders = models.ManyToManyField(Raider, related_name='raids', db_table="gxp_raids_raiders")

    class Meta:
        db_table = "gxp_raids"
