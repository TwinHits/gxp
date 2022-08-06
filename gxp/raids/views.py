from rest_framework import viewsets

from gxp.raids.models import Raid
from gxp.raids.serializers import RaidSerializer

class RaidsViewSet(viewsets.ModelViewSet):
    queryset = Raid.objects.all()
    serializer_class = RaidSerializer
