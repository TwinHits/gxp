from re import I
import uuid

from django.db import models


class Raider(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=12, null=False)
    join_timestamp = models.IntegerField()
    active = models.BooleanField(default=True)
    main = models.ForeignKey("Raider", on_delete=models.CASCADE, null=True)
    experience = models.FloatField(default=0)

    @property
    def isMain(self):
        return self.main is None

    @property
    def isAlt(self):
        return self.main is not None

    @property
    def alts(self):
        if self.isMain:
            return Raider.objects.filter(main=self.id)
        else:
            return []

    class Meta:
        db_table = "gxp_raiders"
        ordering = ["join_timestamp"]


class Alias(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=False)
    raider = models.ForeignKey(
        "Raider", on_delete=models.CASCADE, related_name="aliases"
    )

    class Meta:
        db_table = "gxp_aliases"
        ordering = ["raider"]


class Rename(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    raider = models.ForeignKey(
        Raider, on_delete=models.CASCADE, related_name="renames", null=False
    )
    renamed_from = models.CharField(max_length=12, null=False)

    class Meta:
        db_table = "gxp_renames"
        ordering = ["raider"]
