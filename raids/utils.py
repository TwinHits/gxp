from datetime import datetime
from uuid import UUID, uuid4

from django.db.models import Sum

from raids.models import ExperienceGain, Raid, Raider

class Utils:
    def generateUUID():
        return uuid4()


    def isUUIDValid(uuid):
        try:
            UUID(uuid, version=4)
            return True
        except ValueError:
            return False


    def isValidCharacterName(name):
        return len(name) >= 2 and len(name) <= 12


    def isValidWacraftLogsId(value):
        return True


    def isRaidOptional(raid):
        notOptionalDays = [1, 3]
        raidDate = datetime.fromtimestamp(raid["timestamp"])
        return raidDate.weekday() in notOptionalDays


    def calculate_experience_for_raider(raider):
        result = ExperienceGain.objects.filter(raiderId=raider.id).aggregate(Sum('experienceEventId__value'))
        result = result["experienceEventId__value__sum"]
        if not result:
            return 0
        else:
            return result


    def count_total_raids_for_raider(raider):
        result = Raid.objects.filter(raiders=raider.id).count()
        return result