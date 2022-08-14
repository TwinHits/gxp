from ast import alias
from django.db.models import Sum

from gxp.experience.models import ExperienceGain
from gxp.raids.models import Raid, Raider

class RaiderUtils:
    def is_valid_character_name(name):
        return len(name) >= 2 and len(name) <= 12


    def calculate_experience_for_raider(raider):
        result = ExperienceGain.objects.filter(raiderId=raider.id).aggregate(Sum('experienceEventId__value'))
        result = result["experienceEventId__value__sum"]
        if not result:
            return 0
        else:
            return result


    def count_total_raids_for_raider(raider):
        result = Raid.objects.filter(raiders=raider.id).count()
        return result


    def get_raider_for_name(name):
        try:
            return Raider.objects.get(name=name)
        except Raider.DoesNotExist:
            filter = Raider.objects.filter(aliases__name=name)
            if filter.exists():
                return filter.first()
        
        return None
