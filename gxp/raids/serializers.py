from rest_framework import serializers
from gxp.raids.constants import ValidationErrors
from gxp.raids.models import Raid
from gxp.raiders.models import Raider
from gxp.raids.utils import Utils 

class RaidSerializer(serializers.ModelSerializer):
    timestamp = serializers.IntegerField()
    raiders = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all(), many=True)
    warcraftLogsId = serializers.CharField(required=False, allow_blank=True, default="")
    optional = serializers.BooleanField(required=False)

    def validate_timestamp(self, value):
        return value / 1000

    def validate_warcraftLogsId(self, value):
        if not value.isspace():
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