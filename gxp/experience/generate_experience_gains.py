import logging

from django.db.models import Q

from gxp.raiders.models import Raider, SpecialistRole
from gxp.raiders.utils import RaiderUtils

from gxp.experience.models import ExperienceEvent, ExperienceGain, ExperienceLevel
from gxp.experience.constants import ExperienceEventKeys, BossKillZoneMultiplers
from gxp.experience.serializers import ExperienceGainSerializer

from gxp.raids.models import Raid

from gxp.shared.warcraftLogs.interface import WarcraftLogsInterface
from gxp.shared.ironforgeAnalyzer.interface import IronforgeAnalyzerInterface
from gxp.shared.raidHelper.interface import RaidHelperInterface


class GenerateExperienceGainsForRaid:
    def __init__(self, raid):
        self.raid = raid
        self.logsCode = self.raid.log.logsCode
        self.split_run = self.raid.log.split_run

        self.timestamps_by_enounter_name = {}

        self.corrected_encounter_names = {
            "Terestrian Illhoof": "Terestian Illhoof",
            "Zul'jin": "Zul'Jin",
            "The Iron Council": "The Assembly of Iron",
            "Northrend Beasts": "The Northrend Beasts",
            "The Northrend Beasts'": "The Northrend Beasts",
        }

        self.raid_start_timestamp = self.raid.timestamp
        self.raid_end_timestamp = None

        self.start_of_expansion = 1665633600 * 1000

        self.consumes_exception_encounters = [
            "Flame Leviathan",
        ]

    def generate_all(self):
        if self.raid_start_timestamp > self.start_of_expansion:
            logging.info(f"Calculating GXP for {self.logsCode}...\n ---")
            self.boss_kill_and_complete_raid_experience()
            self.sign_ups_raid_experience()
            self.performance_experience()
            self.decay_per_boss()
            self.reserve_per_boss()
        else:
            self.calculate_experience_last_expansion()

        self.calculate_experience_for_raiders(True)
        logging.info(f"GXP completed for {self.logsCode}.\n ---")

    def get_experienceEvent_id_for_parse_percent(self, parse_percent):
        if parse_percent <= 25:
            return ExperienceEventKeys.LOW_PERFORMER_EVENT_ID
        elif parse_percent <= 50:
            return ExperienceEventKeys.MID_PERFORMER_EVENT_ID
        elif parse_percent <= 75:
            return ExperienceEventKeys.HIGH_PERFORMER_EVENT_ID
        elif parse_percent <= 100:
            return ExperienceEventKeys.TOP_PERFORMER_EVENT_ID

    def correct_encounter_name(self, encounter_name):
        correct_encounter_name = self.corrected_encounter_names.get(encounter_name)
        if correct_encounter_name:
            return correct_encounter_name
        else:
            return encounter_name

    def boss_kill_and_complete_raid_experience(self):
        logging.info(f"Calculating boss kill and raid complete GXP for {self.logsCode}...")

        report = WarcraftLogsInterface.get_raid_kills_by_report_id(
            self.logsCode
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
                    ExperienceEventKeys.BOSS_KILL_EVENT_ID,
                    raider.id,
                    raid_id=self.raid.id,
                    timestamp=tokens.get("enounter_end_timestamp"),
                    tokens=tokens,
                    value=GenerateExperienceGainsForRaid.get_boss_kill_experience_for_zone(self.raid.zone),
                )
                # Since Ironforge Pro Analyzer no longer exists, just add food and flask GXP after the boss kill exp
                ExperienceGainSerializer.create_experience_gain(
                    ExperienceEventKeys.FLASK_ON_EVENT_ID,
                    raider.id,
                    raid_id=self.raid.id,
                    timestamp=tokens.get("enounter_end_timestamp")+1,
                    tokens=tokens,
                )
                ExperienceGainSerializer.create_experience_gain(
                    ExperienceEventKeys.FOOD_ON_EVENT_ID,
                    raider.id,
                    raid_id=self.raid.id,
                    timestamp=tokens.get("enounter_end_timestamp")+2,
                    tokens=tokens,
                )

            if len(participating_encounters) >= number_of_encounters:
                complete_raid_tokens = {
                    "zone": self.raid.zone,
                }
                ExperienceGainSerializer.create_experience_gain(
                    ExperienceEventKeys.COMPLETE_RAID_EVENT_ID,
                    raider.id,
                    raid_id=self.raid.id,
                    timestamp=self.raid_end_timestamp,
                    tokens=complete_raid_tokens,
                )

    def sign_ups_raid_experience(self):
        logging.info(f"Calculating sign up GXP for {self.logsCode}...")

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
                pk=ExperienceEventKeys.SIGNED_UP_ACCURATELY_EVENT_ID
            )
            sign_up_experience_value = encounters_count * sign_up_experience_event.value

            if not response or response.get("status") == "failed":
                logging.error(
                    f"Failed to get event details from event id {self.raid.log.raidHelperEventId} for logs code {self.logsCode} ."
                )
                logging.error(response)
                return

            sign_ups = response.get("signups")
            for sign_up in sign_ups:
                # Who is this sign up?
                name = sign_up.get("name")
                raider = RaiderUtils.get_raider_for_name(name)
                if not raider:
                    logging.error(f"Did not find raider for name {name}. Add {name} as an alias for the correct raider.")
                    continue

                # What was the raider's sign up?
                sign_up_state = sign_up.get("class")
                signed_absent = sign_up_state == "Absence"
                signed_tentative = sign_up_state == "Tentative"
                signed_late = sign_up_state == "Late"
                signed_bench = sign_up_state == "Bench"
                signed_attending = (
                    not signed_absent and not signed_tentative and not signed_late and not signed_bench
                )
                if signed_attending:
                    sign_up_state = "Attending"
                if signed_bench:
                    sign_up_state = "Reserve"
                tokens["sign_up"] = sign_up_state

                # is this raider in the attending raiders?
                if raider in self.raid.raiders.all():
                    # If signed up at all and in raid, then +
                    ExperienceGainSerializer.create_experience_gain(
                        ExperienceEventKeys.SIGNED_UP_ACCURATELY_EVENT_ID,
                        raider.id,
                        raid_id=self.raid.id,
                        timestamp=timestamp,
                        tokens=tokens,
                        value=sign_up_experience_value,
                    )

                # since they are not in the attending raiders, then they are absent. Did they mark absent or bench or are a reserve?
                elif (signed_absent or signed_bench or raider in self.raid.log.reserve_raiders.all()):
                    ExperienceGainSerializer.create_experience_gain(
                        ExperienceEventKeys.SIGNED_UP_ACCURATELY_EVENT_ID,
                        raider.id,
                        raid_id=self.raid.id,
                        timestamp=timestamp,
                        tokens=tokens,
                        value=sign_up_experience_value,
                    )


    def performance_experience(self):
        logging.info(f"Calculating performance GXP for {self.logsCode}...")

        ranking_types = ['dps', 'hps', 'tanks']
        for ranking_type in ranking_types:
            rankings = (
                WarcraftLogsInterface.get_performance_by_report_id(self.logsCode, ranking_type)
                .get("rankings")
                .get("data")
            )

            if len(rankings) == 0:
                logging.warning(f"{self.logsCode} has no parses.")

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
                        f"{self.logsCode} is missing timestamp by encounter name for {encounter_name} for rankings. Add {encounter_name} as the key to `corrected_encounter_names` with a value from {self.timestamps_by_enounter_name}"
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
                    if (event_id == ExperienceEventKeys.HEALER_TANK_LOW_PERFORMER_EVENT_ID and (ranking_type in ['hps', 'tanks'] or SpecialistRole.objects.filter(raider=raider.id, encounter=encounter_name))):
                        event_id = ExperienceEventKeys.HEALER_TANK_LOW_PERFORMER_EVENT_ID

                    ExperienceGainSerializer.create_experience_gain(
                        event_id,
                        raider.id,
                        raid_id=self.raid.id,
                        timestamp=timestamp,
                        tokens=tokens,
                    )

    def decay_per_boss(self):
        logging.info(f"Calculating GXP decay for {self.logsCode}...")
        logging.info(f"{self.logsCode} is {'a' if self.split_run else 'not a'} split run.")

        encounters_count = len(self.timestamps_by_enounter_name)
        tokens = {
            "encounters_count": encounters_count,
        }

        decay_experience_event = ExperienceEvent.objects.get(
            pk=ExperienceEventKeys.DECAY_PER_BOSS_EVENT_ID
        )
        decay_experience_value = encounters_count * decay_experience_event.value
        timestamp = (
            self.raid_end_timestamp + 1
        )

        # If it's a split run, skip decay since we can't tell who was in the other run
        raiders_to_decay = []
        if not self.split_run:
            all_raider_mains = [raider for raider in Raider.objects.filter(main=None) if raider.human_joined <= self.raid.timestamp]
            raiders_to_decay = all_raider_mains
        else:
            raiders_to_decay = self.raid.raiders.all()

        for raider in raiders_to_decay:
            if raider.experience != ExperienceLevel.objects.get_experience_floor() and raider.experience != 0:
                consecutive_missed_raids = Raid.objects.get_count_of_consecutive_raids_missed_for_raider(raider)
                tokens["consecutive_missed_raids"] = consecutive_missed_raids

                decay_multiplier = 1 + consecutive_missed_raids/10
                decay_experience_value_multipled = decay_experience_value * decay_multiplier
                ExperienceGainSerializer.create_experience_gain(
                    ExperienceEventKeys.DECAY_PER_BOSS_EVENT_ID,
                    raider.id,
                    raid_id=self.raid.id,
                    timestamp=timestamp,
                    tokens=tokens,
                    value=decay_experience_value_multipled,
                )

    def reserve_per_boss(self):
        logging.info(f"Calculating reserve GXP for {self.logsCode}...")

        encounters_count = len(self.timestamps_by_enounter_name)
        tokens = {
            "encounters_count": encounters_count,
        }

        reserve_experience_event = ExperienceEvent.objects.get(
            pk=ExperienceEventKeys.RESERVE_PER_BOSS_EVENT_ID
        )
        reserve_experience_value = encounters_count * reserve_experience_event.value
        timestamp = (
            self.raid_end_timestamp + 2
        )
        for raider in self.raid.log.reserve_raiders.all():
            ExperienceGainSerializer.create_experience_gain(
                ExperienceEventKeys.RESERVE_PER_BOSS_EVENT_ID,
                raider.id,
                raid_id=self.raid.id,
                timestamp=timestamp,
                tokens=tokens,
                value=reserve_experience_value,
            )

    def calculate_experience_last_expansion(self):
        logging.info(f"Calculating GXP for a previous expansion raid {self.logsCode}...")

        tokens = {"zone": self.raid.zone}
        for raider in self.raid.raiders.all():
            ExperienceGainSerializer.create_experience_gain(
                ExperienceEventKeys.PREVIOUS_EXPANSION_RAID_EVENT_ID,
                raider.id,
                raid_id=self.raid.id,
                timestamp=self.raid_start_timestamp,
                tokens=tokens,
            )
        return

    @staticmethod
    def get_boss_kill_experience_for_zone(zone):

        experience_event_value = ExperienceEvent.objects.get(pk=ExperienceEventKeys.BOSS_KILL_EVENT_ID).value
        multipler = BossKillZoneMultiplers.by_raid[zone]
        return experience_event_value * multipler

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
            if False and gain.multiplied:
                new_experience = experience + (gain.experience * experience_multipler)
            if gain.experienceEvent.id == "MAIN_CHANGE":
                new_experience = gain.experience;
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
        logging.info(f'Recalculating GXP for {"active" if active else "all"} raiders...')

        if active is not None:
            raiders = Raider.objects.filter(active=active)
        else:
            raiders = Raider.objects.all()

        for raider in raiders:
            GenerateExperienceGainsForRaid.calculate_experience_for_raider(raider)

        logging.info(f'GXP recalculation for {"active" if active else "all"} raiders complete.')
