from tkinter import W
from gxp.raiders.models import Alt, Raider
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
        raiders = []
        for character in report.get("rankedCharacters"):
            name = character.get("name")
            raider = Raider.objects.filter(name=name).first()
            if not raider:
                isAlt = Alt.objects.filter(name=name).first()
                if isAlt:
                    raider = Raider.objects.get(pk=isAlt.id)

            if not raider:
                raider = RaiderSerializer.create_raider(name) 

            if raider:
                raiders.append(raider)

        return raiders