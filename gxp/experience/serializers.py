from rest_framework import serializers
from gxp.experience.models import ExperienceEvent, ExperienceGain, ExperienceLevel
from gxp.raiders.models import Raider
from gxp.shared.utils import SharedUtils


class ExperienceEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExperienceEvent
        fields = ['id', 'description', 'value', 'key']

    def create(self, validated_data):
        return ExperienceEvent.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.key = validated_data.get('key', instance.key)
        instance.description = validated_data.get('description', instance.description)
        instance.value = validated_data.get('value', instance.value)

        instance.save()
        return instance


class ExperienceGainSerializer(serializers.ModelSerializer):
    experienceEventId = serializers.PrimaryKeyRelatedField(queryset=ExperienceEvent.objects.all())
    raiderId = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all())
    timestamp = serializers.IntegerField(required=False)

    class Meta:
        model = ExperienceGain
        fields = ['id', 'experienceEventId', 'raiderId', 'timestamp']

    def create(self, validated_data):
        if not validated_data.get("timestamp"):
            validated_data["timestamp"] = SharedUtils.get_now_timestamp()

        return ExperienceGain.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.experienceEventId = validated_data.get('experienceEventId', instance.experienceEventId)
        instance.raiderId = validated_data.get('raiderId', instance.raiderId)

        instance.save()
        return instance

    @staticmethod
    def create_experience_gain(experience_event_id, raider_id):
        experience_gain_serializer = ExperienceGainSerializer(data={
            "experienceEventId": experience_event_id,
            "raiderId": raider_id,
        })
        experience_gain_serializer.is_valid(raise_exception=True);
        experience_gain_serializer.save()


class ExperienceLevelSerializer(serializers.ModelSerializer):

    class Meta:
        model = ExperienceLevel
        fields = ['id', 'name', 'experience_required']

    def create(self, validated_data):
        return ExperienceLevel.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.experience_required = validated_data.get('experience_required', instance.experience_required)

        instance.save()
        return instance