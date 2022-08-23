import json

from rest_framework import viewsets

from gxp.raiders.models import Alias, Raider
from gxp.raiders.serializers import RaiderSerializer, AliasSerializer


class RaidersViewSet(viewsets.ModelViewSet):
    queryset = Raider.objects.all()
    serializer_class = RaiderSerializer

    def get_queryset(self):
        active = self.request.query_params.get("active")
        if active is not None:
            active= json.loads(active)
            self.queryset = self.queryset.filter(active=active)

        name = self.request.query_params.get("name")
        if name is not None:
            self.queryset = self.queryset.filter(name=name)

        return self.queryset

class AliasesViewSet(viewsets.ModelViewSet):
    queryset = Alias.objects.all()
    serializer_class = AliasSerializer
