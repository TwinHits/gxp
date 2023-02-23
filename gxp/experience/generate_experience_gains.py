import logging

from django.db.models import Q

from gxp.raiders.models import Raider, SpecialistRole
from gxp.experience.models import ExperienceEvent, ExperienceGain, ExperienceLevel

from gxp.experience.serializers import ExperienceGainSerializer
from gxp.raids.models import Raid

from gxp.shared.warcraftLogs.interface import WarcraftLogsInterface
from gxp.shared.ironforgeAnalyzer.interface import IronforgeAnalyzerInterface
from gxp.shared.raidHelper.interface import RaidHelperInterface

from gxp.raiders.utils import RaiderUtils


class GenerateExperienceGainsForRaid:
    def __init__(self, raid):
        self.raid = raid

        self.complete_raid_event_id = "COMPLETE_RAID"

        self.boss_kill_event_id = "BOSS_KILL"
        self.missed_boss_kill_event_id = "MISSED_BOSS_KILL"

        self.food_on_event_id = "BOSS_KILL_FOOD"
        self.food_off_event_id = "BOSS_KILL_NO_FOOD"
        self.flask_on_event_id = "BOSS_KILL_FLASK"
        self.flask_off_event_id = "BOSS_KILL_NO_FLASK"

        self.signed_up_accurately_event_id = "SIGNED_UP_ACCURATELY"
        self.signed_up_inaccurately_event_id = "SIGNED_UP_INACCURATELY"

        self.top_performer_event_id = "TOP_PERFORMANCE"
        self.high_performer_event_id = "HIGH_PERFORMANCE"
        self.mid_performer_event_id = "MID_PERFORMANCE"
        self.low_performer_event_id = "LOW_PERFORMANCE"
        self.healer_tank_low_performer_event_id = "HEALER_TANK_LOW_PERFORMANCE"

        self.decay_per_boss_event_id = "DECAY_PER_BOSS"
        self.reserve_per_boss_event_id = "RESERVE_PER_BOSS"

        self.previous_expansion_raid_event_id = "PREV_EXPAC_RAID"

        self.timestamps_by_enounter_name = {}

        self.corrected_encounter_names = {
            "Terestrian Illhoof": "Terestian Illhoof",
            "Zul'jin": "Zul'Jin",
        }

        self.raid_start_timestamp = self.raid.timestamp
        self.raid_end_timestamp = None

        self.start_of_expansion = 1665633600 * 1000

    def generate_all(self):
        if self.raid_start_timestamp > self.start_of_expansion:
            self.boss_kill_and_complete_raid_experience()
            self.flask_and_consumes_raid_experience()
            self.sign_ups_raid_experience()
            self.performance_experience()
            self.decay_per_boss()
            self.reserve_per_boss()
        else:
            self.calculate_experience_last_expansion()

        self.calculate_experience_for_raiders(True)

    def get_experienceEvent_id_for_parse_percent(self, parse_percent):
        if parse_percent <= 25:
            return self.low_performer_event_id
        elif parse_percent <= 50:
            return self.mid_performer_event_id
        elif parse_percent <= 75:
            return self.high_performer_event_id
        elif parse_percent <= 100:
            return self.top_performer_event_id

    def correct_encounter_name(self, encounter_name):
        correct_encounter_name = self.corrected_encounter_names.get(encounter_name)
        if correct_encounter_name:
            return correct_encounter_name
        else:
            return encounter_name

    def boss_kill_and_complete_raid_experience(self):

        report = WarcraftLogsInterface.get_raid_kills_by_report_id(
            self.raid.log.logsCode
        )

        actors = report.get("masterData").get(
            "actors"
        )  # array of player name and data id
        names_by_data_id = {actor.get("id"): actor.get("name") for actor in actors}
        kill_count_by_name = {}

        self.raid_start_timestamp = report.get("startTime")
        self.raid_end_timestamp = report.get("endTime")

        # Get map of encounters completed by name using an array of tokens' length to keep count
        encounter_logs = report.get("fights")  # array of fight name and player data ids
        for encounter_log in encounter_logs:
            enounter_end_timestamp = self.raid_start_timestamp + encounter_log.get(
                "endTime"
            )
            encounter_name = encounter_log.get("name")
            self.timestamps_by_enounter_name[encounter_name] = enounter_end_timestamp
            tokens = {
                "encounter": encounter_name,
                "enounter_end_timestamp": enounter_end_timestamp,  # endtime is ms since report started
            }
            for data_id in encounter_log.get("friendlyPlayers"):
                name = names_by_data_id[data_id]
                if not kill_count_by_name.get(name):
                    kill_count_by_name[name] = []
                kill_count_by_name[name].append(tokens)

        # Create exp for each encounter completed, implicitly leaving out encounters they did not participate in
        number_of_encounters = len(encounter_logs)
        for name, participating_encounters in kill_count_by_name.items():
            raider = RaiderUtils.get_raider_for_name(name)
            for tokens in reversed(participating_encounters):
                ExperienceGainSerializer.create_experience_gain(
                    self.boss_kill_event_id,
                    raider.id,
                    raid_id=self.raid.id,
                    timestamp=tokens.get("enounter_end_timestamp"),
                    tokens=tokens,
                )
            if len(participating_encounters) >= number_of_encounters:
                complete_raid_tokens = {
                    "zone": self.raid.zone,
                }
                ExperienceGainSerializer.create_experience_gain(
                    self.complete_raid_event_id,
                    raider.id,
                    raid_id=self.raid.id,
                    timestamp=self.raid_end_timestamp,
                    tokens=complete_raid_tokens,
                )

    def flask_and_consumes_raid_experience(self):

        consumes_report = IronforgeAnalyzerInterface.get_consumes_for_report(
            self.raid.log.logsCode
        )

        # build encounter look up map of kills
        fights = consumes_report.get("fights")
        encounter_by_fight_id = {}
        for fight in fights:
            if (
                fight.get("kill") and fight.get("name") != "Overall"
            ):  # only care about kills and not overall
                result = [
                    fs for fs in fight.get("fights") if fs.get("kill")
                ]  # don't care about the attempts
                result = result[0]
                if len(result):
                    name = result.get("name")
                    id = result.get("id")
                    encounter_by_fight_id[id] = {
                        "name": name,
                        "timestamp": self.raid.timestamp + result.get("end"),
                    }

        # check if raider has flasks and consumes for each kill
        consumes_data = consumes_report.get("data")
        for consumes in consumes_data:
            encounter = encounter_by_fight_id.get(consumes.get("fight"))
            if encounter:  # only for fight ids we want want from above
                for data in consumes.get("data"):
                    raider_name = data.get("actor").get("name")
                    raider = RaiderUtils.get_raider_for_name(raider_name)
                    food = len(data.get("buffs").get("food"))
                    flask = len(data.get("buffs").get("flask"))

                    tokens = {
                        "encounter": encounter.get(
                            "name"
                        )  # Ironforge Analyzer uses different encounter names :(
                    }

                    flask_timestamp = (
                        encounter.get("timestamp")
                        + 1  # Offset time a bit for nice history ordering
                    )
                    if flask:
                        ExperienceGainSerializer.create_experience_gain(
                            self.flask_on_event_id,
                            raider.id,
                            raid_id=self.raid.id,
                            timestamp=flask_timestamp,
                            tokens=tokens,
                        )
                    else:
                        ExperienceGainSerializer.create_experience_gain(
                            self.flask_off_event_id,
                            raider.id,
                            raid_id=self.raid.id,
                            timestamp=flask_timestamp,
                            tokens=tokens,
                        )

                    food_timestamp = encounter.get("timestamp") + 2
                    if food:
                        ExperienceGainSerializer.create_experience_gain(
                            self.food_on_event_id,
                            raider.id,
                            raid_id=self.raid.id,
                            timestamp=food_timestamp,
                            tokens=tokens,
                        )
                    else:
                        ExperienceGainSerializer.create_experience_gain(
                            self.food_off_event_id,
                            raider.id,
                            raid_id=self.raid.id,
                            timestamp=food_timestamp,
                            tokens=tokens,
                        )

    def sign_ups_raid_experience(self):

        if self.raid.log.raidHelperEventId:
            response = RaidHelperInterface.get_sign_ups_for_event_id(
                self.raid.log.raidHelperEventId
            )

            encounters_count = len(self.timestamps_by_enounter_name)
            timestamp = (
                self.raid.timestamp - 1  # Offset time a bit for nice history ordering
            )
            tokens = {
                "zone": self.raid.zone,
                "encounters_count": encounters_count,
            }

            sign_up_experience_event = ExperienceEvent.objects.get(
                pk=self.signed_up_accurately_event_id
            )
            sign_up_experience_value = encounters_count * sign_up_experience_event.value

            if response.get("status") == "failed":
                logging.error(
                    f"Failed to get event details from event id {self.raid.log.raidHelperEventId} for logs code {self.raid.log.logsCode} ."
                )
                logging.error(response)
                return

            sign_ups = response.get("signups")
            for sign_up in sign_ups:
                name = sign_up.get("name")
                sign_up_state = sign_up.get("class")
                signed_absent = sign_up_state == "Absence"
                signed_tentative = sign_up_state == "Tentative"
                signed_late = sign_up_state == "Late"
                signed_attending = (
                    not signed_absent and not signed_tentative and not signed_late
                )
                if signed_attending:
                    sign_up_state = "Attending"
                tokens["sign_up"] = sign_up_state

                # is this name in the attending raiders?
                next = False
                for raider in self.raid.raiders.all():
                    if RaiderUtils.is_name_for_raider(name, raider):
                        raider_main = RaiderUtils.get_raider_for_name(name)
                        # If signed up at all and in raid, then +
                        ExperienceGainSerializer.create_experience_gain(
                            self.signed_up_accurately_event_id,
                            raider_main.id,
                            raid_id=self.raid.id,
                            timestamp=timestamp,
                            tokens=tokens,
                            value=sign_up_experience_value,
                        )
                        next = True
                        break

                # since they are not in the attending raiders, then they are absent. Did they mark absent?
                if not next and signed_absent:
                    raider = RaiderUtils.get_raider_for_name(name)
                    if raider:
                        # If signed absent and not in raid, then +
                        ExperienceGainSerializer.create_experience_gain(
                            self.signed_up_accurately_event_id,
                            raider.id,
                            raid_id=self.raid.id,
                            timestamp=timestamp,
                            tokens=tokens,
                            value=sign_up_experience_value,
                        )
                        next = True

                if not next:
                    raider = RaiderUtils.get_raider_for_name(name)
                    if not raider:
                        logging.error(f"DID NOT FIND RAIDER FOR {name}")

    def performance_experience(self):
        ranking_types = ['dps', 'hps', 'tanks']
        for ranking_type in ranking_types:
            rankings = (
                WarcraftLogsInterface.get_performance_by_report_id(self.raid.log.logsCode, ranking_type)
                .get("rankings")
                .get("data")
            )

            if len(rankings) == 0:
                logging.warning(f"{self.raid.log.logsCode} has no parses.")

            for encounter in rankings:
                encounter_name = self.correct_encounter_name(
                    encounter.get("encounter").get("name")
                )
                tokens = {"encounter": encounter_name}
                timestamp = self.timestamps_by_enounter_name.get(encounter_name)
                if timestamp:
                    timestamp = timestamp + 3  # Offset time a bit for nice history ordering
                else:
                    # This parse is not for an encounter, so skip
                    logging.warning(
                        f"{self.raid.log.logsCode} is missing timestamp by encounter name for {encounter_name} for rankings."
                    )
                    continue

                if ranking_type == 'dps':
                    ranking_raiders = encounter.get("roles").get("dps").get("characters")
                elif ranking_type == 'hps':
                    ranking_raiders = encounter.get("roles").get("healers").get("characters")
                elif ranking_type == 'tanks':
                    ranking_raiders = encounter.get("roles").get("tanks").get("characters")

                for ranking_raider in ranking_raiders:
                    raider = RaiderUtils.get_raider_for_name(ranking_raider.get("name"))
                    ilvl_percent = ranking_raider.get("bracketPercent")
                    parse_percent = ranking_raider.get("rankPercent")

                    # take the higher of the two percents
                    higher_percent = max(ilvl_percent, parse_percent)

                    # don't parse grey for tanks, healers, specialists
                    event_id = self.get_experienceEvent_id_for_parse_percent(higher_percent)
                    if (event_id == self.low_performer_event_id and (ranking_type in ['hps', 'tanks'] or SpecialistRole.objects.filter(raider=raider.id, encounter=encounter_name))):
                        event_id = self.healer_tank_low_performer_event_id

                    ExperienceGainSerializer.create_experience_gain(
                        event_id,
                        raider.id,
                        raid_id=self.raid.id,
                        timestamp=timestamp,
                        tokens=tokens,
                    )

    def decay_per_boss(self):
        encounters_count = len(self.timestamps_by_enounter_name)
        tokens = {
            "encounters_count": encounters_count,
        }

        decay_experience_event = ExperienceEvent.objects.get(
            pk=self.decay_per_boss_event_id
        )
        decay_experience_value = encounters_count * decay_experience_event.value
        timestamp = (
            self.raid_end_timestamp + 1
        )

        all_raider_mains = [raider for raider in Raider.objects.filter(main=None) if raider.human_joined <= self.raid.timestamp]
        for raider in all_raider_mains:
            ExperienceGainSerializer.create_experience_gain(
                self.decay_per_boss_event_id,
                raider.id,
                raid_id=self.raid.id,
                timestamp=timestamp,
                tokens=tokens,
                value=decay_experience_value,
            )

    def reserve_per_boss(self):
        encounters_count = len(self.timestamps_by_enounter_name)
        tokens = {
            "encounters_count": encounters_count,
        }

        reserve_experience_event = ExperienceEvent.objects.get(
            pk=self.reserve_per_boss_event_id
        )
        reserve_experience_value = encounters_count * reserve_experience_event.value
        timestamp = (
            self.raid_end_timestamp + 2
        )
        for raider in self.raid.reserve_raiders.all():
            ExperienceGainSerializer.create_experience_gain(
                self.reserve_per_boss_event_id,
                raider.id,
                raid_id=self.raid.id,
                timestamp=timestamp,
                tokens=tokens,
                value=reserve_experience_value,
            )

    def calculate_experience_last_expansion(self):
        tokens = {"zone": self.raid.zone}
        for raider in self.raid.raiders.all():
            ExperienceGainSerializer.create_experience_gain(
                self.previous_expansion_raid_event_id,
                raider.id,
                raid_id=self.raid.id,
                timestamp=self.raid_start_timestamp,
                tokens=tokens,
            )
        return

    @staticmethod
    def update_gain_for_event_changes(gain):
        """
        If the event id is in a specific list of event ids that calculate based on something like encounter count, check if they need to be recalculated.
        """
        DECAY_PER_BOSS_ID = "DECAY_PER_BOSS";
        SIGNED_UP_ACCURATELY_ID = "SIGNED_UP_ACCURATELY"

        if gain.experienceEvent.id == DECAY_PER_BOSS_ID:
            event = ExperienceEvent.objects.get(pk=DECAY_PER_BOSS_ID)
            raid = Raid.objects.get(pk=gain.raid.id)
            new_value = event.value * raid.encounters_completed
            if new_value != gain.value:
                gain.value = new_value
                gain.save()

        elif gain.experienceEvent.id == SIGNED_UP_ACCURATELY_ID:
            event = ExperienceEvent.objects.get(pk=SIGNED_UP_ACCURATELY_ID)
            raid = Raid.objects.get(pk=gain.raid.id)
            new_value = event.value * raid.encounters_completed
            if new_value != gain.value:
                gain.value = new_value
                gain.save()

        return gain

    @staticmethod
    def calculate_experience_for_raider(raider):
        gains = ExperienceGain.objects.filter(
            Q(raid__isnull=True) | Q(raid__optional=False), raider=raider
        )
        experience_multipler = RaiderUtils.calculate_experience_multipler_for_raider(
            raider
        )
        highest_experience_level_experience_required = (
            ExperienceLevel.objects.last().experience_required
        )
        experience_floor = ExperienceLevel.objects.all()[1].experience_required
        experience_ceiling = highest_experience_level_experience_required + 75

        floor = 0
        experience = 0
        for gain in gains:
            gain = GenerateExperienceGainsForRaid.update_gain_for_event_changes(gain)

            if False and gain.multiplied:
                new_experience = experience + (gain.experience * experience_multipler)
            if gain.experienceEvent.id == "MAIN_CHANGE":
                new_experience = gain.experience;
                print(f"Changed mains, exp set to {new_experience} from {experience}")
            else:
                new_experience = experience + gain.experience

            if new_experience < floor:
                experience = floor
            elif new_experience > experience_ceiling:
                experience = experience_ceiling
            else:
                experience = new_experience

            # once you get above the second lowest level, don't drop below it again
            if experience > experience_floor:
                floor = experience_floor

        raider.experience = experience
        raider.save()

    @staticmethod
    def calculate_experience_for_raiders(active=None):
        if active is not None:
            raiders = Raider.objects.filter(active=active)
        else:
            raiders = Raider.objects.all()

        for raider in raiders:
            GenerateExperienceGainsForRaid.calculate_experience_for_raider(raider)
