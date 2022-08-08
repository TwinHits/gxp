import time
from uuid import UUID, uuid4

class SharedUtils:
    def get_now_timestamp():
        return time.time()

    def generateUUID():
        return uuid4()

    def isUUIDValid(uuid):
        try:
            UUID(uuid, version=4)
            return True
        except ValueError:
            return False
