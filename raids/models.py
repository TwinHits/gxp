import uuid
from django.db import models

class Raid(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.IntegerField()
    zone = models.CharField(max_length=100, blank=True, default='')
    warcraftLogsId = models.CharField(max_length=100, blank=True, default='')
    optional = models.BooleanField(default=True)
    raiders = models.ManyToManyField('Raider', related_name='raids', db_table="gxp_raids_raiders")

    class Meta:
        db_table = "gxp_raids"


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


class ExperienceEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=260, blank=False)
    value = models.IntegerField()

    class Meta:
        db_table = "gxp_experience_events"


class ExperienceGain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experienceEventId = models.ForeignKey('ExperienceEvent', on_delete=models.CASCADE, related_name="experienceGains")
    raiderId = models.ForeignKey('Raider', on_delete=models.CASCADE, related_name="experienceGains")
    timestamp = models.IntegerField()

    class Meta:
        db_table = "gxp_experience_gains"