from rest_framework import serializers

from gxp.experience.models import ExperienceEvent, ExperienceGain, ExperienceLevel
from gxp.raids.models import Raid
from gxp.raiders.models import Raider
from gxp.shared.utils import SharedUtils
from gxp.experience.utils import ExperienceUtils


class ExperienceEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienceEvent
        fields = ["id", "description", "value", "template", "multiplied"]

    def create(self, validated_data):
        return ExperienceEvent.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.description = validated_data.get("description", instance.description)
        instance.value = validated_data.get("value", instance.value)
        instance.template = validated_data.get("template", instance.template)
        instance.multiplied = validated_data.get("multiplied", instance.multiplied)

        instance.save()
        return instance


class ExperienceGainSerializer(serializers.ModelSerializer):
    experienceEvent = serializers.PrimaryKeyRelatedField(
        queryset=ExperienceEvent.objects.all()
    )
    raider = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all())
    timestamp = serializers.IntegerField(required=False)
    tokens = serializers.JSONField(required=False)
    raid = serializers.PrimaryKeyRelatedField(
        queryset=Raid.objects.all(), required=False
    )
    description = serializers.SerializerMethodField()
    value = serializers.FloatField(required=False)

    def get_description(self, experience_gain):
        description = ExperienceUtils.get_description_from_template(experience_gain)
        return description

    def to_representation(self, instance):
        data = super(ExperienceGainSerializer, self).to_representation(instance)
        data.update({"value": instance.experience})
        return data

    class Meta:
        model = ExperienceGain
        fields = [
            "id",
            "experienceEvent",
            "raider",
            "timestamp",
            "tokens",
            "description",
            "raid",
            "value",
        ]

    def create(self, validated_data):
        if not validated_data.get("timestamp"):
            validated_data["timestamp"] = SharedUtils.get_now_timestamp()

        return ExperienceGain.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.experienceEvent = validated_data.get(
            "experienceEvent", instance.experienceEvent
        )
        instance.raider = validated_data.get("raider", instance.raider)
        instance.value = validated_data.get("value", instance.value)

        instance.save()
        return instance

    @staticmethod
    def create_experience_gain(
        experience_event_id,
        raider_id,
        raid_id=None,
        timestamp=None,
        tokens=None,
        value=None,
    ):
        data = {}

        data["experienceEvent"] = experience_event_id
        data["raider"] = raider_id
        if raid_id:
            data["raid"] = raid_id
        if tokens:
            data["tokens"] = tokens
        if timestamp:
            data["timestamp"] = timestamp
        if value is not None:
            data["value"] = value

        experience_gain_serializer = ExperienceGainSerializer(data=data)
        experience_gain_serializer.is_valid(raise_exception=True)
        experience_gain_serializer.save()


class ExperienceLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExperienceLevel
        fields = ["id", "name", "experience_required"]

    def create(self, validated_data):
        return ExperienceLevel.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.experience_required = validated_data.get(
            "experience_required", instance.experience_required
        )

        instance.save()
        return instance
