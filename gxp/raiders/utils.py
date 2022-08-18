from ast import alias
from django.db.models import Sum

from gxp.experience.models import ExperienceGain
from gxp.raids.models import Raid, Raider
from gxp.shared.utils import SharedUtils

class RaiderUtils:
    def is_valid_character_name(name):
        return len(name) >= 2 and len(name) <= 12


    def calculate_experience_for_raider(raider):
        result = ExperienceGain.objects.filter(raider=raider.id).aggregate(Sum('experienceEvent__value'))
        result = result["experienceEvent__value__sum"]
        if not result:
            return 0
        else:
            return result


    def count_total_raids_for_raider(raider):
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


    def is_name_for_raider(name, raider):
        # Check if the name is the raider, an alt, or an alias

        # Is the name the raider
        if name == raider.name:
            return True

        # is the name an alt
        alts = [alt for alt in raider.alts.all() if alt.alt.name == name];
        if len(alts):
            return True


        aliases = [alias for alias in raider.aliases.all() if alias.name == name];
        if len(aliases):
            return True
    
        return False
