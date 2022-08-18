from rest_framework import serializers

from gxp.raids.constants import ValidationErrors
from gxp.raids.models import Log, Raid
from gxp.raids.utils import RaidUtils 
from gxp.raiders.models import Raider

from gxp.shared.warcraftLogs.interface import WarcraftLogsInterface
from gxp.shared.warcraftLogs.utils import WarcraftLogsUtils
from gxp.shared.utils import SharedUtils

from gxp.experience.generate_experience_gains import GenerateExperienceGainsForRaid

class LogSerializer(serializers.ModelSerializer):
    logsCode = serializers.CharField(required=True, allow_blank=False)
    raidHelperEventId = serializers.CharField(required=False, allow_blank=True)
    active = serializers.BooleanField(required=False, default=True)
    timestamp = serializers.IntegerField(required=False)

    def validate_logsCode(self, value):
        if not WarcraftLogsUtils.is_valid_warcraft_logs_id(value):
            raise serializers.ValidationError(ValidationErrors.INVALID_WARCRAFT_LOGS_ID)

        return value

    class Meta:
        model = Log
        fields = ['logsCode', 'raidHelperEventId', 'active', 'timestamp', 'zone']
        
    def create(self, validated_data):
        if Log.objects.filter(logsCode=validated_data.get("logsCode")):
            raise serializers.ValidationError(ValidationErrors.WARCRAFT_LOGS_ID_LOG_ALREADY_EXISTS) 

        if not validated_data.get("timestamp") or not validated_data.get("zone"):
            raid_report = WarcraftLogsInterface.get_raid_by_report_id(validated_data["logsCode"])
            if not validated_data.get("timestamp"):
                validated_data["timestamp"] = WarcraftLogsUtils.get_start_timestamp_from_report(raid_report)
            if not validated_data.get("zone"):
                validated_data["zone"] = WarcraftLogsUtils.get_zone_name_from_report(raid_report)

        log = Log.objects.create(**validated_data)
        return log

    def update(self, instance, validated_data):
        instance.raidHelperEventId = validated_data.get('raidHelperEventId', instance.raidHelperEventId)
        instance.active = validated_data.get('active', instance.active)

        instance.save()
        return instance
        
    
class RaidSerializer(serializers.ModelSerializer):
    optional = serializers.BooleanField(required=False)
    raiders = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all(), required=False, many=True)
    timestamp = serializers.IntegerField(required=False)
    log = LogSerializer(required=False) 
           
    class Meta:
        model = Raid
        fields = ['id', 'log', 'optional', 'raiders', 'timestamp']

    def create(self, validated_data):
        raiders = []
        if 'log' in validated_data:

            logs_code = validated_data["log"].get("logsCode")
                
            if Raid.objects.filter(log__logsCode=logs_code):
                raise serializers.ValidationError(ValidationErrors.WARCRAFT_LOGS_ID_RAID_ALREADY_EXISTS) 

            if not validated_data['log'].get("active"): 
                raise serializers.ValidationError(ValidationErrors.LOG_INACTIVE) 

            try:
                log = Log.objects.get(pk=logs_code)
                log.raidHelperEventId = validated_data['log'].get('raidHelperEventId')
                log.save()
                validated_data['log'] = log

                if 'timestamp' not in validated_data:
                    validated_data['timestamp'] = log.timestamp
                if 'zone' not in validated_data:
                    validated_data['zone'] = log.zone

                raiders = WarcraftLogsInterface.get_raiders_by_report_id(logs_code)
            except Exception as err:
                raise serializers.ValidationError(err)

        if 'timestamp' not in validated_data:
            validated_data['timestamp'] = SharedUtils.get_now_timestamp()

        if 'optional' not in validated_data:
            validated_data["optional"] = RaidUtils.is_raid_optional(validated_data.get("timestamp"))

        raid = Raid.objects.create(**validated_data)
        for raider in raiders:
            raid.raiders.add(raider)
        raid.save()

        GenerateExperienceGainsForRaid(raid).generate_all()

        return raid


    def update(self, instance, validated_data):
        instance.optional = validated_data.get('optional', instance.optional)

        instance.save()
        return instance