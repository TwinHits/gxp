from rest_framework import viewsets

from gxp.raiders.models import Raider, Alt
from gxp.raiders.serializers import RaiderSerializer, AltSerializer


class RaidersViewSet(viewsets.ModelViewSet):
    queryset = Raider.objects.all()
    serializer_class = RaiderSerializer


class AltsViewSet(viewsets.ModelViewSet):
    queryset = Alt.objects.all()
    serializer_class = AltSerializer
