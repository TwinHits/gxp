import logging

class RaidHelperUtils:
    @staticmethod
    def handle_error(err):
        logging.error("Raid Helper Error: ")
        logging.error(err)