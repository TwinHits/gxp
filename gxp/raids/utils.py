from datetime import datetime
from gxp.raids.models import Raid

class RaidUtils:
    def is_raid_optional(timestamp):
        notOptionalDays = [1, 3]
        raidDate = datetime.fromtimestamp(timestamp / 1000)
        return raidDate.weekday() in notOptionalDays
    

    def count_total_raids_for_raider(raider):
        result = Raid.objects.filter(raiders=raider.id).count()
        return result