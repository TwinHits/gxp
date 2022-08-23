from typing import Set
from gxp.raiders.models import Raider
from gxp.raiders.serializers import RaiderSerializer
from gxp.raiders.utils import RaiderUtils


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

        # array of player name and data id
        actors = report.get("masterData").get("actors")
        names_by_data_id = {actor.get("id"): actor.get("name") for actor in actors}

        # For each enounter, add participating names to set
        participating_names_set = set()
        encounter_logs = report.get("fights")  # array of fight name and player data ids
        for encounter_log in encounter_logs:
            for data_id in encounter_log.get("friendlyPlayers"):
                name = names_by_data_id[data_id]
                participating_names_set.add(name)

        raiders = []
        for name in participating_names_set:
            try:
                raider = RaiderUtils.get_raider_for_name(name)
                raiders.append(raider)
            except Raider.DoesNotExist:
                raider = RaiderSerializer.create_raider(name, join_timestamp=timestamp)
                raiders.append(raider)

        return raiders

    def get_number_of_enocunters_from_report(report):
        return len(report.get("fights"))
