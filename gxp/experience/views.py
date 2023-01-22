from rest_framework import viewsets

from gxp.experience.models import ExperienceEvent, ExperienceGain, ExperienceLevel
from gxp.experience.serializers import (
    ExperienceEventSerializer,
    ExperienceGainSerializer,
    ExperienceLevelSerializer,
)

from gxp.raiders.models import Raider

from gxp.shared.permissions import IsAuthenticatedOrRead


class ExperienceEventsViewSet(viewsets.ModelViewSet):
    queryset = ExperienceEvent.objects.all()
    serializer_class = ExperienceEventSerializer
    permission_classes = [IsAuthenticatedOrRead]


class ExperienceGainsViewSet(viewsets.ModelViewSet):
    queryset = ExperienceGain.objects.all()
    serializer_class = ExperienceGainSerializer
    permission_classes = [IsAuthenticatedOrRead]

    def get_queryset(self):
        raiderId = self.request.query_params.get("raiderId")
        if raiderId:
            raider = Raider.objects.get(pk=raiderId)
            raiders = list(raider.alts)
            raiders.append(raider)
            self.queryset = self.queryset.filter(raider__in=raiders)

        experienceEventId = self.request.query_params.get("experienceEvent")
        if experienceEventId:
            self.queryset = self.queryset.filter(experienceEvent=experienceEventId)

        return self.queryset


class ExperienceLevelsViewSet(viewsets.ModelViewSet):
    queryset = ExperienceLevel.objects.all()
    serializer_class = ExperienceLevelSerializer
    permission_classes = [IsAuthenticatedOrRead]
