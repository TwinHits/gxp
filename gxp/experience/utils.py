from gxp.experience.serializers import ExperienceGainSerializer

class ExperienceUtils:
    def generate_experience_gains_for_raid(raid):

        def complete_entire_raid(raid):
            event_id = "e0ff8926-f79f-4fdd-bbfd-414d31756854" # How are methods linked to ids?
            raiders = raid.raiders.all()
            for raider in raiders:
                raider_id = raider.id
                ExperienceGainSerializer.create_experience_gain(event_id, raider_id)

        complete_entire_raid(raid)