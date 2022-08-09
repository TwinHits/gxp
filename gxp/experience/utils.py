from django.forms import model_to_dict

from gxp.shared.utils import SharedUtils

class ExperienceUtils:

    def get_description_from_template(experience_gain):
        tokens = {**model_to_dict(experience_gain), **model_to_dict(experience_gain.raiderId), **model_to_dict(experience_gain.experienceEventId), **experience_gain.tokens}
        tokens["date"] = SharedUtils.format_datetime_as_date(SharedUtils.get_datetime_from_timestamp(tokens["timestamp"]))
        tokens["datetime"] = SharedUtils.format_datetime_as_date_and_time(SharedUtils.get_datetime_from_timestamp(tokens["timestamp"]))
        return experience_gain.experienceEventId.template.format(**tokens)