from ntpath import join
from gxp.raiders.models import Raider
from gxp.raiders.serializers import RaiderSerializer


class WarcraftLogsUtils:
    def is_valid_warcraft_logs_id(id):
        return True

    def get_message_from_errors(dict):
        message = ""
        errors = dict.get("errors")
        for error in errors:
            message += error.get("message") + " "
        return message

    def get_start_timestamp_from_report(report):
        return report.get("startTime")

    def get_zone_name_from_report(report):
        return report.get("zone").get("name")

    def get_or_create_raiders_from_report(report):
        timestamp = WarcraftLogsUtils.get_start_timestamp_from_report(report)
        raiders = []
        for character in report.get("rankedCharacters"):
            name = character.get("name")
            try:
                raider = Raider.objects.get(name=name)
                raiders.append(raider)
            except Raider.DoesNotExist:
                raider = RaiderSerializer.create_raider(name, join_timestamp=timestamp)
                raiders.append(raider)

        return raiders

    def get_number_of_enocunters_from_report(report):
        return len(report.get('fights'))