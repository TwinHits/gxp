from django.db.models import Sum

from gxp.experience.models import ExperienceGain
from gxp.raiders.models import Raider

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