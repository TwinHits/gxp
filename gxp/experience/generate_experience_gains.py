from gxp.raiders.models import Raider
from gxp.experience.models import ExperienceEvent

from gxp.experience.serializers import ExperienceGainSerializer

from gxp.shared.warcraftLogs.interface import WarcraftLogsInterface
from gxp.shared.ironforgeAnalyzer.interface import IronforgeAnalyzerInterface
from gxp.shared.raidHelper.interface import RaidHelperInterface

from gxp.raiders.utils import RaiderUtils

class GenerateExperienceGainsForRaid:
    def __init__(self, raid):
        self.raid = raid

        self.complete_raid_event_id = ExperienceEvent.objects.get(key="COMPLETE_RAID").id
        self.boss_kill_event_id = ExperienceEvent.objects.get(key="BOSS_KILL").id
        self.food_on_event_id = ExperienceEvent.objects.get(key="BOSS_KILL_FOOD").id
        self.food_off_event_id = ExperienceEvent.objects.get(key="BOSS_KILL_NO_FOOD").id
        self.flask_on_event_id = ExperienceEvent.objects.get(key="BOSS_KILL_FLASK").id
        self.flask_off_event_id = ExperienceEvent.objects.get(key="BOSS_KILL_NO_FLASK").id
        self.signed_up_accurately_event_id = ExperienceEvent.objects.get(key="SIGNED_UP_ACCURATELY").id
        self.signed_up_inaccurately_event_id = ExperienceEvent.objects.get(key="SIGNED_UP_INACCURATELY").id
        
        self.name_to_raider = {}
        for raider in self.raid.raiders.all():
            self.name_to_raider[raider.name] = raider


    def generate_all(self):
        self.boss_kill_and_complete_raid_experience()
        self.flask_and_consumes_raid_experience()
        self.sign_ups_raid_experience()
        


    def boss_kill_and_complete_raid_experience(self):

        kill_logs = WarcraftLogsInterface.get_raid_kills_by_report_id(self.raid.log.logsCode)

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
            try:
                raider = Raider.objects.get(name=name)
                for tokens in reversed(participating_kills):
                    ExperienceGainSerializer.create_experience_gain(self.boss_kill_event_id, raider.id, raid_id=self.raid.id, timestamp=tokens.get("kill_timestamp"), tokens=tokens)
                if len(participating_kills) >= number_of_kills:
                    complete_raid_tokens = {
                        "zone": self.raid.zone,
                    }
                    ExperienceGainSerializer.create_experience_gain(self.complete_raid_event_id, raider.id, raid_id=self.raid.id, timestamp=raid_end_timestamp, tokens=complete_raid_tokens)

            except Raider.DoesNotExist:
                print(f"{name} is not a raider!")

    def flask_and_consumes_raid_experience(self):

        consumes_report = IronforgeAnalyzerInterface.get_consumes_for_report(self.raid.log.logsCode)

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
                        "timestamp": self.raid.timestamp + result.get("end")
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
                        ExperienceGainSerializer.create_experience_gain(self.flask_on_event_id, raider.id, raid_id=self.raid.id, timestamp=flask_timestamp, tokens=tokens)
                    else:
                        ExperienceGainSerializer.create_experience_gain(self.flask_off_event_id, raider.id, raid_id=self.raid.id, timestamp=flask_timestamp, tokens=tokens)

                    food_timestamp = encounter.get("timestamp") + 2
                    if food: 
                        ExperienceGainSerializer.create_experience_gain(self.food_on_event_id, raider.id, raid_id=self.raid.id, timestamp=food_timestamp,tokens=tokens)
                    else:
                        ExperienceGainSerializer.create_experience_gain(self.food_off_event_id, raider.id, raid_id=self.raid.id, timestamp=food_timestamp, tokens=tokens)


    def sign_ups_raid_experience(self):

        if self.raid.log.raidHelperEventId:
            response = RaidHelperInterface.get_sign_ups_for_event_id(self.raid.log.raidHelperEventId)

            timestamp = self.raid.timestamp - 1 # Offset time a bit for nice history ordering
            tokens = {
                "zone": self.raid.zone
            }

            if response.get("status") == "failed":
                print(response)
                return

            sign_ups = response.get("signups")
            for sign_up in sign_ups:
                name = sign_up.get("name")
                sign_up_state = sign_up.get("class")
                signed_absent = sign_up_state == "Absence"
                signed_tentative = sign_up_state == "Tentative"
                signed_late = sign_up_state == "Late"
                signed_attending = not signed_absent and not signed_tentative and not signed_late
                if signed_attending: sign_up_state = "Attending"
                tokens["sign_up"] = sign_up_state

                """
                pattern = re.compile('[^a-zA-Z0-9/]')
                name = pattern.sub('', name) 
                name_parts = name.split("/")
                """

                # is this name in the attending raiders?
                for raider in self.name_to_raider.values():
                    next = False
                    if RaiderUtils.is_name_for_raider(name, raider):
                        # If signed up at all and in raid, then +
                        ExperienceGainSerializer.create_experience_gain(self.signed_up_accurately_event_id, raider.id, raid_id=self.raid.id, timestamp=timestamp, tokens=tokens)
                        next = True
                        break
                
                # since they are not in the attending raiders, then they are absent. Did they mark absent?
                if not next and signed_absent:
                    raider = RaiderUtils.get_raider_for_name(name)
                    if raider:
                        # If signed absent and not in raid, then +
                        ExperienceGainSerializer.create_experience_gain(self.signed_up_accurately_event_id, raider.id, raid_id=self.raid.id, timestamp=timestamp, tokens=tokens)
                        next = True

                # The harder stuff like late, tentative, bench, etc
                if not next:
                    raider = RaiderUtils.get_raider_for_name(name)
                    if not raider:
                        print(f"DID NOT FIND RAIDER FOR {name}")