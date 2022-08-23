
from gxp.experience.models import ExperienceLevel
from gxp.raids.models import Raid
from gxp.raiders.models import Raider, Rename
from gxp.shared.utils import SharedUtils


class RaiderUtils:
    def is_valid_character_name(name):
        return len(name) >= 2 and len(name) <= 12

    def calculate_experience_multipler_for_raider(raider, raider_raids=None):
        # (Current raids / total guild raids) + 1
        if raider_raids is None:
            raider_raids = RaiderUtils.count_raids_for_raider(raider)
        total_guild_raids = Raid.objects.filter(optional=False).count()
        if total_guild_raids > 0:
            return (raider_raids / total_guild_raids) + 1
        else: 
            return 1

    def calculate_experience_level_for_raider(raider):
        experience_level = ExperienceLevel.objects.filter(experience_required__lte=raider.experience).last()
        return experience_level

    def count_raids_for_raider(raider):
        result = Raid.objects.filter(raiders=raider.id, optional=False).count()
        return result

    def count_total_weeks_for_raider(raider):
        return SharedUtils.get_weeks_since_timestamp(raider.join_timestamp)

    def get_raider_for_name(name):
        if name is None:
            return None

        try:
            return Raider.objects.get(name=name)
        except Raider.DoesNotExist:
            filter = Rename.objects.filter(renamed_from=name)
            if filter.exists():
                return filter.first().raider
            
            filter = Raider.objects.filter(aliases__name=name)
            if filter.exists():
                return filter.first()

        return None

    # Check if the name is the raider, an , or an alias
    def is_name_for_raider(name, raider):

        # Is the name the raider
        if name == raider.name:
            return True
        
        # Is the name an old name
        renames = [rename for rename in raider.renames.all() if rename.renamed_from == name]
        if len(renames):
            return True

        # Is the name an alt
        alts = [alt for alt in raider.alts if alt.name == name]
        if len(alts):
            return True


        # Is the name an alias
        aliases = [alias for alias in raider.aliases.all() if alias.name == name]
        if len(aliases):
            return True

        return False
