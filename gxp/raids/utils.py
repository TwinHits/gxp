from datetime import datetime

from gxp.raiders.models import Raider
from gxp.experience.models import ExperienceEvent
from gxp.experience.serializers import ExperienceGainSerializer
from gxp.shared.warcraftLogs.interface import WarcraftLogsInterface
from gxp.shared.ironforgeAnalyzer.interface import IronforgeAnalyzerInterface

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
            raid_start_timestamp = kill_logs.get("startTime")
            raid_end_timestamp = kill_logs.get("endTime")
            for kill in kills:
                kill_timestamp = raid_start_timestamp + kill.get("endTime")
                tokens = {
                    "encounter": kill.get("name"),
                    "kill_timestamp": kill_timestamp # endtime is ms since report started
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
                    ExperienceGainSerializer.create_experience_gain(boss_kill_event_id, raider.id, timestamp=tokens.get("kill_timestamp"), tokens=tokens)
                if len(participating_kills) >= number_of_kills:
                    complete_raid_tokens = {
                        "zone": raid.zone,
                    }
                    ExperienceGainSerializer.create_experience_gain(complete_raid_event_id, raider.id, timestamp=raid_end_timestamp, tokens=complete_raid_tokens)

        def flask_and_consumes_raid_experience(raid):
            food_on_event_id = ExperienceEvent.objects.get(key="BOSS_KILL_FOOD").id
            food_off_event_id = ExperienceEvent.objects.get(key="BOSS_KILL_NO_FOOD").id
            flask_on_event_id = ExperienceEvent.objects.get(key="BOSS_KILL_FLASK").id
            flask_off_event_id = ExperienceEvent.objects.get(key="BOSS_KILL_NO_FLASK").id

            consumes_report = IronforgeAnalyzerInterface.get_consumes_for_report(raid.warcraftLogsId)

            # build encounter look up map of kills
            fights = consumes_report.get("fights")
            encounter_by_fight_id = {}
            for fight in fights:
                if fight.get("kill") and fight.get("name") != "Overall": # only care about kills and not overall
                    result = [fs for fs in fight.get("fights") if fs.get("kill")] # don't care about the attempts
                    result = result[0]
                    if len(result):
                        name = result.get("name")
                        id = result.get("id")
                        encounter_by_fight_id[id] = {
                            "name": name,
                            "timestamp": raid.timestamp + result.get("end")
                        }

            # check if raider has flasks and consumes for each kill
            consumes_data = consumes_report.get("data")
            for consumes in consumes_data:
                encounter = encounter_by_fight_id.get(consumes.get("fight"))
                if encounter: # only for fight ids we want want from above
                    for data in consumes.get("data"):
                        raider_name = data.get("actor").get("name")
                        raider = Raider.objects.get(name=raider_name)
                        food = len(data.get("buffs").get("food"))
                        flask = len(data.get("buffs").get("flask"))

                        tokens = { "encounter": encounter.get("name") }
                        
                        flask_timestamp = encounter.get("timestamp") + 1 # Offset time a bit for nice history ordering
                        if flask:
                            ExperienceGainSerializer.create_experience_gain(flask_on_event_id, raider.id, timestamp=flask_timestamp, tokens=tokens)
                        else:
                            ExperienceGainSerializer.create_experience_gain(flask_off_event_id, raider.id, timestamp=flask_timestamp, tokens=tokens)

                        food_timestamp = encounter.get("timestamp") + 2
                        if food: 
                            ExperienceGainSerializer.create_experience_gain(food_on_event_id, raider.id, timestamp=food_timestamp,tokens=tokens)
                        else:
                            ExperienceGainSerializer.create_experience_gain(food_off_event_id, raider.id, timestamp=food_timestamp, tokens=tokens)


        try:
            boss_kill_and_complete_raid_experience(raid)
            flask_and_consumes_raid_experience(raid)
        except Exception as err:
            print(err)