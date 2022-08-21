from statistics import mode
import uuid
from django.db import models

from gxp.raids.models import Raid
from gxp.raiders.models import Raider


class ExperienceEvent(models.Model):
    id = models.CharField(primary_key=True, max_length=255)
    description = models.CharField(max_length=255, null=False)
    template = models.CharField(max_length=255)
    value = models.IntegerField()

    class Meta:
        db_table = "gxp_experience_events"
        ordering = ["id"]


class ExperienceGain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experienceEvent = models.ForeignKey(
        ExperienceEvent, on_delete=models.CASCADE, related_name="experienceGains"
    )
    raider = models.ForeignKey(
        Raider, on_delete=models.CASCADE, related_name="experienceGains"
    )
    raid = models.ForeignKey(
        Raid, on_delete=models.CASCADE, related_name="experienceGains", null=True
    )
    timestamp = models.IntegerField()
    tokens = models.JSONField(default=dict)

    class Meta:
        db_table = "gxp_experience_gains"
        ordering = ["timestamp"]


class ExperienceLevel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    experience_required = models.IntegerField()

    class Meta:
        db_table = "gxp_experience_levels"
        ordering = ["experience_required"]
