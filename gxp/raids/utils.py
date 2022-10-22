from datetime import datetime
from pytz import timezone

class RaidUtils:
    def is_raid_optional(timestamp):
        notOptionalDays = [1, 3]
        raidDate = datetime.fromtimestamp(timestamp / 1000)
        raidDate = timezone('US/Eastern').localize(raidDate)
        return raidDate.weekday() not in notOptionalDays
