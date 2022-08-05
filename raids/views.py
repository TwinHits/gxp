from django.http import Http404, HttpResponseBadRequest
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import JSONParser
from rest_framework import viewsets

from raids.models import Alt, ExperienceEvent, Raid, Raider
from raids.serializers import AltSerializer, ExperienceEventSerializer, RaidSerializer, RaiderSerializer

class RaidsViewSet(viewsets.ModelViewSet):
    queryset = Raid.objects.all()
    serializer_class = RaidSerializer


class RaidersViewSet(viewsets.ModelViewSet):
    queryset = Raider.objects.all()
    serializer_class = RaiderSerializer


class ExperienceEventsViewSet(viewsets.ModelViewSet):
    queryset = ExperienceEvent.objects.all()
    serializer_class = ExperienceEventSerializer


class AltsViewSet(viewsets.ModelViewSet):
    queryset = Alt.objects.all()
    serializer_class = AltSerializer