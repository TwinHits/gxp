from datetime import datetime


class RaidUtils:
    def is_raid_optional(timestamp):
        notOptionalDays = [1, 3]
        raidDate = datetime.fromtimestamp(timestamp / 1000)
        return raidDate.weekday() not in notOptionalDays
