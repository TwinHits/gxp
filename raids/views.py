from rest_framework import viewsets

from raids.models import Alt, ExperienceEvent, ExperienceGain, Raid, Raider
from raids.serializers import AltSerializer, ExperienceEventSerializer, RaidSerializer, RaiderSerializer, ExperienceGainSerializer

class RaidsViewSet(viewsets.ModelViewSet):
    queryset = Raid.objects.all()
    serializer_class = RaidSerializer


class RaidersViewSet(viewsets.ModelViewSet):
    queryset = Raider.objects.all()
    serializer_class = RaiderSerializer


class AltsViewSet(viewsets.ModelViewSet):
    queryset = Alt.objects.all()
    serializer_class = AltSerializer


class ExperienceEventsViewSet(viewsets.ModelViewSet):
    queryset = ExperienceEvent.objects.all()
    serializer_class = ExperienceEventSerializer


class ExperienceGainViewSet(viewsets.ModelViewSet):
    queryset = ExperienceGain.objects.all()
    serializer_class = ExperienceGainSerializer