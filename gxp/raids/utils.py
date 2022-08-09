from datetime import datetime

from gxp.raiders.models import Raider
from gxp.experience.models import ExperienceEvent
from gxp.experience.serializers import ExperienceGainSerializer
from gxp.shared.warcraftLogs.interface import WarcraftLogsInterface

class RaidUtils:
    def is_raid_optional(timestamp):
        notOptionalDays = [1, 3]
        raidDate = datetime.fromtimestamp(timestamp / 1000)
        return raidDate.weekday() in notOptionalDays
    

    def generate_experience_gains_for_raid(raid):

        def boss_kill_and_complete_raid_experience(raid):
            complete_raid_event_id = ExperienceEvent.objects.get(key="COMPLETE_RAID").id
            boss_kill_event_id = ExperienceEvent.objects.get(key="BOSS_KILL").id

            kill_logs = WarcraftLogsInterface.get_raid_kills_by_report_id(raid.warcraftLogsId)

            actors = kill_logs.get("masterData").get("actors") # array of player name and data id
            players_by_data_id = {actor.get("id"):actor.get("name") for actor in actors}
            kill_count_by_name = {}

            kills = kill_logs.get("fights") # array of fight name and player data ids
            starttime = kill_logs.get("startTime")
            for kill in kills:
                tokens = {
                    "encounter": kill.get("name"),
                    "timestamp": starttime + kill.get("endTime") # endtime is ms since report started
                }
                for data_id in kill.get("friendlyPlayers"):
                    name = players_by_data_id[data_id]
                    if not kill_count_by_name.get(name):
                        kill_count_by_name[name] = []
                    kill_count_by_name[name].append(tokens)

            number_of_kills = len(kills)
            for name, participating_kills in kill_count_by_name.items():
                raider = Raider.objects.get(name=name)
                for tokens in reversed(participating_kills):
                    ExperienceGainSerializer.create_experience_gain(boss_kill_event_id, raider.id, tokens=tokens)
                if len(participating_kills) >= number_of_kills:
                    complete_raid_tokens = {
                        "zone": raid.zone,
                        "timestamp": raid.timestamp,
                    }
                    ExperienceGainSerializer.create_experience_gain(complete_raid_event_id, raider.id, tokens=complete_raid_tokens)

        bexperience_requiredoss_kill_and_complete_raid_experience(raid)