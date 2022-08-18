from ntpath import join
from rest_framework import serializers

from gxp.raiders.models import Alias, Alt, Raider

from gxp.raids.constants import ValidationErrors
from gxp.raiders.utils import RaiderUtils 
from gxp.shared.utils import SharedUtils 


class AltSerializer(serializers.ModelSerializer):
    main = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all())
    alt = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all())

    class Meta:
        model = Alt
        fields = ['id', 'main', 'alt']

    def create(self, validated_data):
        return Alt.objects.create(**validated_data)

    def update(self, instance, validated_data):

        instance.save()
        return instance


class AliasSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    raider = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all())

    class Meta:
        model = Alias
        fields = ['id', 'name', 'raider']

    def create(self, validated_data):
        return Alias.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)

        instance.save()
        return instance


class RaiderSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    join_timestamp = serializers.IntegerField(required=False)
    experience = serializers.SerializerMethodField()
    totalRaids = serializers.SerializerMethodField()
    totalWeeks = serializers.SerializerMethodField()
    alts = serializers.SerializerMethodField()
    aliases = AliasSerializer(many=True, required=False)

    def validate_name(self, value):
        if not RaiderUtils.is_valid_character_name(value):
            raise serializers.ValidationError(ValidationErrors.INVALID_CHARACTER_NAME)

        existingName = Raider.objects.filter(name=value).first()
        if existingName:
            raise serializers.ValidationError(ValidationErrors.NAME_ALREADY_EXISTS)

        return value

    def get_experience(self, raider):
        return RaiderUtils.calculate_experience_for_raider(raider)

    def get_totalRaids(self, raider):
        return RaiderUtils.count_total_raids_for_raider(raider)

    def get_totalWeeks(self, raider):
        return RaiderUtils.count_total_weeks_for_raider(raider)

    def get_alts(self, raider):
        alts = [RaiderSerializer(Raider.objects.get(pk=alt.alt.id)).data for alt in raider.alts.all()]
        return alts

    class Meta:
        model = Raider
        fields = ['id', 'name', 'join_timestamp', 'alts', 'experience', 'totalRaids', 'totalWeeks', 'aliases']

    def create(self, validated_data):

        if not validated_data.get("join_timestamp"):
            validated_data["join_timestamp"] = SharedUtils.get_now_timestamp()

        return Raider.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)

        instance.save()
        return instance

    @staticmethod 
    def create_raider(name, join_timestamp=None):
        data = { "name": name}
        if join_timestamp: data['join_timestamp'] = join_timestamp

        raider_serializer = RaiderSerializer(data=data)
        raider_serializer.is_valid(raise_exception=True);
        return raider_serializer.save()