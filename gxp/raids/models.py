import uuid
from django.db import models

from gxp.raiders.models import Raider


class Log(models.Model):
    logsCode = models.CharField(primary_key=True, max_length=255, editable=False)
    timestamp = models.IntegerField()
    zone = models.CharField(max_length=255, null=True, default="")
    raidHelperEventId = models.CharField(max_length=255, null=True, default="")
    active = models.BooleanField(default=True)
    optional = models.BooleanField(default=True)
    reserve_raiders = models.ManyToManyField(
        Raider, related_name="reserve_logs", db_table="gxp_logs_reserve_raiders"
    )

    class Meta:
        db_table = "gxp_logs"
        ordering = ["-timestamp"]


class Raid(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.IntegerField()
    zone = models.CharField(max_length=255, null=True, default="")
    optional = models.BooleanField(default=True)
    raiders = models.ManyToManyField(
        Raider, related_name="raids", db_table="gxp_raids_raiders"
    )
    log = models.ForeignKey(
        Log, on_delete=models.CASCADE, related_name="raid", null=True
    )
    encounters_completed = models.IntegerField()

    class Meta:
        db_table = "gxp_raids"
        ordering = ["-timestamp"]
