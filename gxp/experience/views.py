from rest_framework import viewsets

from gxp.experience.models import ExperienceEvent, ExperienceGain
from gxp.experience.serializers import ExperienceEventSerializer, ExperienceGainSerializer


class ExperienceEventsViewSet(viewsets.ModelViewSet):
    queryset = ExperienceEvent.objects.all()
    serializer_class = ExperienceEventSerializer


class ExperienceGainsViewSet(viewsets.ModelViewSet):
    queryset = ExperienceGain.objects.all()
    serializer_class = ExperienceGainSerializer