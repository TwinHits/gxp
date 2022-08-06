from rest_framework import serializers
from gxp.experience.models import ExperienceEvent, ExperienceGain
from gxp.raiders.models import Raider


class ExperienceEventSerializer(serializers.ModelSerializer):
    description = serializers.CharField()
    value = serializers.IntegerField()

    class Meta:
        model = ExperienceEvent
        fields = ['id', 'description', 'value']

    def create(self, validated_data):
        return ExperienceEvent.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.description = validated_data.get('description', instance.description)
        instance.value = validated_data.get('value', instance.value)

        instance.save()
        return instance


class ExperienceGainSerializer(serializers.ModelSerializer):
    experienceEventId = serializers.PrimaryKeyRelatedField(queryset=ExperienceEvent.objects.all())
    raiderId = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all())
    timestamp = serializers.IntegerField()

    def validate_timestamp(self, value):
        return value / 1000

    class Meta:
        model = ExperienceGain
        fields = ['id', 'experienceEventId', 'raiderId', 'timestamp']

    def create(self, validated_data):
        return ExperienceGain.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.experienceEventId = validated_data.get('experienceEventId', instance.experienceEventId)
        instance.raiderId = validated_data.get('raiderId', instance.raiderId)

        instance.save()
        return instance