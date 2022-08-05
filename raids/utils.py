from datetime import date, datetime
from string import whitespace
from uuid import UUID, uuid4

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