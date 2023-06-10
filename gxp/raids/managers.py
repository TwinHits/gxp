from django.db import models

class RaidManager(models.Manager):
    def get_count_of_consecutive_raids_missed_for_raider(self, raider):
        raids = self.all().order_by("-timestamp")
        count = 0
        for raid in raids:
            if raider in raid.raiders.all():
                return count
            else:
                count = count + 1
        return count