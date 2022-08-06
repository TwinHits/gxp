import uuid

from django.db import models


class Raider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=12, blank=False)
    joinTimestamp = models.IntegerField()

    class Meta:
        db_table = "gxp_raiders"

class Alt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=12, blank=False)
    raiderId = models.ForeignKey('Raider', on_delete=models.CASCADE, related_name='alts')

    class Meta:
        db_table = "gxp_alts"