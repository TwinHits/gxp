from sqlite3 import Timestamp
from rest_framework import serializers

from gxp.raids.constants import ValidationErrors
from gxp.raids.models import Raid
from gxp.raids.utils import RaidUtils 
from gxp.raiders.models import Raider
from gxp.shared.warcraftLogs.interface import WarcraftLogsInterface
from gxp.shared.warcraftLogs.utils import WarcraftLogsUtils

class RaidSerializer(serializers.ModelSerializer):
    warcraftLogsId = serializers.CharField(required=False, allow_blank=True, default="")
    optional = serializers.BooleanField(required=False)
    raiders = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all(), required=False, many=True)
    timestamp = serializers.IntegerField(required=False)
    raidHelperEventId = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_warcraftLogsId(self, value):
        if not value.isspace():
            if not WarcraftLogsUtils.is_valid_warcraft_logs_id(value):
                raise serializers.ValidationError(ValidationErrors.INVALID_WARCRAFT_LOGS_ID)

            existingRaid = Raid.objects.filter(warcraftLogsId=value)
            if existingRaid:
                raise serializers.ValidationError(ValidationErrors.WARCRAFT_LOGS_ID_ALREADY_EXISTS)

        return value

    class Meta:
        model = Raid
        fields = ['id', 'warcraftLogsId', 'optional', 'raiders', 'timestamp', 'raidHelperEventId']

    def create(self, validated_data):

        raiders = []
        if 'warcraftLogsId' in validated_data and validated_data["warcraftLogsId"]:
            try:
                raid_report = WarcraftLogsInterface.get_raid_by_report_id(validated_data["warcraftLogsId"])
                validated_data["timestamp"] = WarcraftLogsUtils.get_start_timestamp_from_report(raid_report)
            except Exception as err:
                raise serializers.ValidationError(err)

            validated_data["zone"] = WarcraftLogsUtils.get_zone_name_from_report(raid_report)
            raiders = WarcraftLogsUtils.get_or_create_raiders_from_report(raid_report)

            validated_data["zone"] = WarcraftLogsUtils.get_zone_name_from_report(raid_report)
            raiders = WarcraftLogsUtils.get_or_create_raiders_from_report(raid_report)

        if 'optional' not in validated_data:
            validated_data["optional"] = RaidUtils.is_raid_optional(validated_data.get("timestamp"))

        raid = Raid.objects.create(**validated_data)
        for raider in raiders:
            raid.raiders.add(raider)

        RaidUtils.generate_experience_gains_for_raid(raid)

        return raid


    def update(self, instance, validated_data):
        instance.zone = validated_data.get('zone', instance.zone)
        instance.warcraftLogsId = validated_data.get('code', instance.warcraftLogsId)
        instance.optional = validated_data.get('optional', instance.optional)

        instance.save()
        return instance