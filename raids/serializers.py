from rest_framework import serializers
from raids.constants import ValidationErrors
from raids.models import Alt, ExperienceEvent, Raid, Raider, ExperienceGain
from raids.utils import Utils 

class RaidSerializer(serializers.ModelSerializer):
    timestamp = serializers.IntegerField()
    raiders = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all(), many=True)
    warcraftLogsId = serializers.CharField(required=False, allow_blank=True, default="")
    optional = serializers.BooleanField(required=False)

    def validate_timestamp(self, value):
        return value / 1000

    def validate_warcraftLogsId(self, value):
        if value.isspace():
            if not Utils.isValidWacraftLogsId(value):
                raise serializers.ValidationError(ValidationErrors.INVALID_WARCRAFT_LOGS_ID)

            existingRaid = Raid.objects.filter(warcraftLogsId=value)
            if existingRaid:
                raise serializers.ValidationError(ValidationErrors.WARCRAFT_LOGS_ID_ALREADY_EXISTS)

        return value

    class Meta:
        model = Raid
        fields = ['id', 'zone', 'warcraftLogsId', 'timestamp', 'optional', 'raiders']

    def create(self, validated_data):

        if 'optional' not in validated_data:
            validated_data["optional"] = Utils.isRaidOptional(validated_data)

        raiders = validated_data.get("raiders")
        del validated_data["raiders"]
        raid = Raid.objects.create(**validated_data)
        for raider in raiders:
            raid.raiders.add(raider)

        return raid

    def update(self, instance, validated_data):
        instance.zone = validated_data.get('zone', instance.zone)
        instance.warcraftLogsId = validated_data.get('code', instance.warcraftLogsId)
        instance.optional = validated_data.get('optional', instance.optional)

        instance.save()
        return instance


class AltSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    raiderId = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all())

    def validate_name(self, value):
        if not Utils.isValidCharacterName(value):
            raise serializers.ValidationError(ValidationErrors.INVALID_CHARACTER_NAME)

        existingName = Raider.objects.filter(name=value).first()
        if existingName:
            raise serializers.ValidationError(ValidationErrors.NAME_ALREADY_EXISTS)

        return value

    class Meta:
        model = Alt
        fields = ['id', 'name', 'raiderId']

    def create(self, validated_data):
        return Alt.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)

        instance.save()
        return instance


class RaiderSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    joinTimestamp = serializers.IntegerField()
    alts = AltSerializer(many=True, read_only=True)
    experience = serializers.SerializerMethodField()
    totalRaids = serializers.SerializerMethodField()

    def validate_name(self, value):
        if not Utils.isValidCharacterName(value):
            raise serializers.ValidationError(ValidationErrors.INVALID_CHARACTER_NAME)

        existingName = Raider.objects.filter(name=value).first()
        if existingName:
            raise serializers.ValidationError(ValidationErrors.NAME_ALREADY_EXISTS)

        return value

    def validate_joinTimestamp(self, value):
        return value / 1000 

        
    def get_experience(self, raider):
        return Utils.calculate_experience_for_raider(raider)

    def get_totalRaids(self, raider):
        return Utils.count_total_raids_for_raider(raider)

    class Meta:
        model = Raider
        fields = ['id', 'name', 'joinTimestamp', 'alts', 'experience', 'totalRaids']

    def create(self, validated_data):
        return Raider.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)

        instance.save()
        return instance


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