from datetime import datetime
import time
from uuid import UUID, uuid4

class SharedUtils:
    def get_now_timestamp():
        return time.time()

    def get_datetime_from_timestamp(timestamp):
        return datetime.fromtimestamp(timestamp / 1000)

    def format_datetime_as_date(datetime):
        return datetime.strftime("%m/%d/%Y")

    def format_datetime_as_date_and_time(datetime):
        return datetime.strftime("%m/%d/%Y %I:%M %p")

    def generateUUID():
        return uuid4()

    def isUUIDValid(uuid):
        try:
            UUID(uuid, version=4)
            return True
        except ValueError:
            return False
