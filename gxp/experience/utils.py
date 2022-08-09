from gxp.raiders.models import Raider
from gxp.experience.serializers import ExperienceGainSerializer
from gxp.shared.warcraftLogs.interface import WarcraftLogsInterface

class ExperienceUtils:
    def generate_experience_gains_for_raid(raid):

        def boss_kill_and_complete_raid_experience(raid):
            complete_raid_event_id = "e0ff8926-f79f-4fdd-bbfd-414d31756854"
            boss_kill_event_id = "a1c0026b-f9eb-4d7a-aa3b-a78781a293f1"

            kill_logs = WarcraftLogsInterface.get_raid_kills_by_report_id(raid.warcraftLogsId)

            actors = kill_logs.get("masterData").get("actors") # array of player name and data id
            players_by_data_id = {actor.get("id"):actor.get("name") for actor in actors}
            kill_count_by_name = {}

            kills = kill_logs.get("fights") # array of fight name and player data ids
            number_of_kills = len(kills)
            for kill in kills:
                for data_id in kill.get("friendlyPlayers"):
                    name = players_by_data_id[data_id]
                    if not kill_count_by_name.get(name):
                        kill_count_by_name[name] = 0
                    kill_count_by_name[name] += 1

            for name, kill_count in kill_count_by_name.items():
                raider = Raider.objects.get(name=name)
                if kill_count >= number_of_kills:
                    ExperienceGainSerializer.create_experience_gain(complete_raid_event_id, raider.id)
                for i in range(kill_count):
                    ExperienceGainSerializer.create_experience_gain(boss_kill_event_id, raider.id)

        boss_kill_and_complete_raid_experience(raid)