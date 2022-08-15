import uuid
from django.db import models

from gxp.raiders.models import Raider

class Log(models.Model):
    logsCode = models.CharField(primary_key=True, max_length=255, editable=False)
    timestamp = models.IntegerField()
    zone = models.CharField(max_length=255, blank=True, default='')
    raidHelperEventId = models.CharField(max_length=255, blank=True, default='')
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "gxp_logs"

class Raid(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.IntegerField()
    zone = models.CharField(max_length=255, blank=True, default='')
    optional = models.BooleanField(default=True)
    raiders = models.ManyToManyField(Raider, related_name='raids', db_table="gxp_raids_raiders")
    log = models.ForeignKey(Log, on_delete=models.CASCADE, related_name="raid", null=True)

    class Meta:
        db_table = "gxp_raids"