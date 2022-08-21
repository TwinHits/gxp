from audioop import mul
from django.db.models import Sum
from gxp import experience

from gxp.experience.models import ExperienceGain, ExperienceLevel
from gxp.raids.models import Raid, Raider
from gxp.shared.utils import SharedUtils


class RaiderUtils:
    def is_valid_character_name(name):
        return len(name) >= 2 and len(name) <= 12

    def calculate_experience_for_raider(raider, experience_multipler=None):
        gains = ExperienceGain.objects.filter(raider=raider.id, raid__optional=False)
        highest_experience_level_experience_required = ExperienceLevel.objects.last().experience_required

        if experience_multipler is None:
            experience_multipler = RaiderUtils.calculate_experience_multipler_for_raider(raider)

        experience = 0
        for gain in gains:
            new_experience = experience + (gain.experienceEvent.value * experience_multipler)
            if new_experience < 0:
                experience = 0
            elif new_experience > highest_experience_level_experience_required:
                experience = highest_experience_level_experience_required
            else: 
                experience = new_experience
        return experience 

    def calculate_experience_multipler_for_raider(raider, raider_raids=None):
        # (Current raids / total guild raids) + 1
        if raider_raids is None:
            raider_raids = RaiderUtils.count_raids_for_raider(raider)
        total_guild_raids = Raid.objects.all().count()
        if total_guild_raids > 0:
            return (raider_raids / total_guild_raids) + 1
        else: 
            return 1

    def calculate_experience_level_for_raider(raider, experience=None):
        if experience is None:
            experience = RaiderUtils.calculate_experience_for_raider(raider)

        experience_level = ExperienceLevel.objects.filter(experience_required__lte=experience).last()
        return experience_level

    def count_raids_for_raider(raider):
        result = Raid.objects.filter(raiders=raider.id).count()
        return result

    def count_total_weeks_for_raider(raider):
        return SharedUtils.get_weeks_since_timestamp(raider.join_timestamp)

    def get_raider_for_name(name):
        try:
            return Raider.objects.get(name=name)
        except Raider.DoesNotExist:
            filter = Raider.objects.filter(aliases__name=name)
            if filter.exists():
                return filter.first()

        return None

    # Check if the name is the raider, an alt, or an alias
    def is_name_for_raider(name, raider):

        # Is the name the raider
        if name == raider.name:
            return True

        # is the name an alt
        alts = [alt for alt in raider.alts.all() if alt.alt.name == name]
        if len(alts):
            return True

        aliases = [alias for alias in raider.aliases.all() if alias.name == name]
        if len(aliases):
            return True

        return False
