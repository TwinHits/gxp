import json

from rest_framework import viewsets

from gxp.raiders.models import Alias, Raider, Alt
from gxp.raiders.serializers import RaiderSerializer, AltSerializer, AliasSerializer


class RaidersViewSet(viewsets.ModelViewSet):
    queryset = Raider.objects.all()
    serializer_class = RaiderSerializer

    def get_queryset(self):
        active = self.request.query_params.get("active")
        if active is not None:
            active= json.loads(active)
            self.queryset = self.queryset.filter(active=active)

        return self.queryset

class AltsViewSet(viewsets.ModelViewSet):
    queryset = Alt.objects.all()
    serializer_class = AltSerializer


class AliasesViewSet(viewsets.ModelViewSet):
    queryset = Alias.objects.all()
    serializer_class = AliasSerializer
