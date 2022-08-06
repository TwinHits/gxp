from rest_framework import serializers

from gxp.raiders.models import Alt, Raider

from gxp.raids.constants import ValidationErrors
from gxp.raids.utils import Utils 


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