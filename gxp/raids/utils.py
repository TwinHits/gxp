from datetime import datetime
from pytz import timezone

class RaidUtils:
    def is_raid_optional(timestamp):
        notOptionalDays = [1, 3]
        raidDate = datetime.fromtimestamp(timestamp / 1000, tz=timezone('US/Eastern'))
        return raidDate.weekday() not in notOptionalDays
