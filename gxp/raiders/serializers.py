from rest_framework import serializers
from gxp.experience.serializers import ExperienceLevelSerializer

from gxp.raiders.models import Alias, Raider, Rename, SpecialistRole

from gxp.raids.constants import ValidationErrors
from gxp.raiders.change_mains import change_mains
from gxp.raiders.utils import RaiderUtils
from gxp.shared.utils import SharedUtils


class SpecialistRoleSerializer(serializers.ModelSerializer):
    raider = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all())
    encounter = serializers.CharField(required=True, allow_blank=False)

    class Meta:
        model = SpecialistRole
        fields = ["id", "raider", "encounter"]

    def create(self, validated_data):
        return SpecialistRole.objects.create(**validated_data)


class RenameSerializer(serializers.ModelSerializer):
    renamed_from = serializers.CharField()
    raider = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all())

    class Meta:
        model = Rename
        fields = ["id", "renamed_from", "raider"]

    def create(self, validated_data):
        return Rename.objects.create(**validated_data)


class AliasSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    raider = serializers.PrimaryKeyRelatedField(queryset=Raider.objects.all())

    class Meta:
        model = Alias
        fields = ["id", "name", "raider"]

    def create(self, validated_data):
        return Alias.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)

        instance.save()
        return instance


class RaiderSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    join_timestamp = serializers.IntegerField(required=False)
    totalWeeks = serializers.SerializerMethodField()
    alts = serializers.SerializerMethodField()
    aliases = AliasSerializer(many=True, required=False)
    active = serializers.BooleanField(required=False)
    main = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Raider.objects.all(), allow_null=True, default=None
    )
    renames = RenameSerializer(many=True, required=False)

    def to_representation(self, raider):
        data = super().to_representation(raider)

        total_raids = RaiderUtils.count_raids_for_raider(raider)
        experience_multipler = RaiderUtils.calculate_experience_multipler_for_raider(
            raider, total_raids
        )
        level = ExperienceLevelSerializer(
            RaiderUtils.calculate_experience_level_for_raider(raider)
        ).data
        join_timestamp = raider.human_joined

        data.update(
            {
                "totalRaids": total_raids,
                "experienceMultipler": experience_multipler,
                "experienceLevel": level,
                "join_timestamp": join_timestamp,
            }
        )

        return data

    def validate_name(self, value):
        if not RaiderUtils.is_valid_character_name(value):
            raise serializers.ValidationError(ValidationErrors.INVALID_CHARACTER_NAME)

        return value

    def get_totalWeeks(self, raider):
        return RaiderUtils.count_total_weeks_for_raider(raider)

    def get_alts(self, raider):
        return [alt.id for alt in raider.alts if raider.alts]

    class Meta:
        model = Raider
        fields = [
            "id",
            "name",
            "join_timestamp",
            "totalWeeks",
            "experience",
            "main",
            "alts",
            "aliases",
            "active",
            "renames",
        ]

    def create(self, validated_data):
        existingName = Raider.objects.filter(name=validated_data["name"]).first()
        if existingName:
            raise serializers.ValidationError(ValidationErrors.NAME_ALREADY_EXISTS)

        if not validated_data.get("join_timestamp"):
            validated_data["join_timestamp"] = SharedUtils.get_now_timestamp()

        return Raider.objects.create(**validated_data)

    def update(self, instance, validated_data):

        new_active_state = validated_data.get("active", instance.active)
        if new_active_state != instance.active:
            # Change active state for each alt
            for alt in instance.alts:
                alt.active = new_active_state
                alt.save()
            instance.active = new_active_state

        name = validated_data.get("name", instance.name)
        if name != instance.name:
            if Raider.objects.filter(name=name).exists():
                raise serializers.ValidationError(ValidationErrors.NAME_ALREADY_EXISTS)

            Rename.objects.create(
                **{
                    "raider": instance,
                    "renamed_from": instance.name,
                }
            )
            instance.name = name

        new_main = validated_data.get("main", instance.main)
        if new_main != instance.main:

            if new_main and new_main.isAlt and new_main in instance.alts:
                change_mains(instance, new_main)
            if new_main and new_main.isAlt:
                raise serializers.ValidationError(ValidationErrors.RAIDER_IS_AN_ALT)

            instance.main = new_main

        instance.join_timestamp = validated_data.get("join_timestamp", instance.join_timestamp)

        instance.save()
        return instance

    @staticmethod
    def create_raider(name, join_timestamp=None):
        data = {"name": name}
        if join_timestamp:
            data["join_timestamp"] = join_timestamp

        raider_serializer = RaiderSerializer(data=data)
        raider_serializer.is_valid(raise_exception=True)
        return raider_serializer.save()
