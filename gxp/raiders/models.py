import uuid

from django.db import models


class Raider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=12, blank=False)
    joinTimestamp = models.IntegerField()

    class Meta:
        db_table = "gxp_raiders"
        ordering = ["joinTimestamp"]


class Alt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alt = models.ForeignKey('Raider', on_delete=models.CASCADE, related_name='main')
    main = models.ForeignKey('Raider', on_delete=models.CASCADE, related_name='alts')

    class Meta:
        db_table = "gxp_alts"
        ordering = ["main"]

class Alias(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=False)
    raider = models.ForeignKey('Raider', on_delete=models.CASCADE, related_name='aliases')

    class Meta:
        db_table = "gxp_aliases"
        ordering = ["raider"]