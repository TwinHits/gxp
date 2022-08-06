import uuid
from django.db import models

from gxp.raiders.models import Raider

class ExperienceEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=260, blank=False)
    value = models.IntegerField()

    class Meta:
        db_table = "gxp_experience_events"


class ExperienceGain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    experienceEventId = models.ForeignKey(ExperienceEvent, on_delete=models.CASCADE, related_name="experienceGains")
    raiderId = models.ForeignKey(Raider, on_delete=models.CASCADE, related_name="experienceGains")
    timestamp = models.IntegerField()

    class Meta:
        db_table = "gxp_experience_gains"