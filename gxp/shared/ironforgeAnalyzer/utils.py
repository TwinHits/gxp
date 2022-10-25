import logging

class IronforgeAnalyzerUtils:
    @staticmethod
    def handle_error(err):
        logging.error("Ironforge Analyzer Error: ")
        logging.error(err)
