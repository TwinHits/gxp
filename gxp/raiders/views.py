import json

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from gxp.experience.generate_experience_gains import GenerateExperienceGainsForRaid
from gxp.raiders.models import Alias, Raider
from gxp.raiders.serializers import RaiderSerializer, AliasSerializer
from gxp.shared.permissions import IsAuthenticatedOrRead


class RaidersViewSet(viewsets.ModelViewSet):
    queryset = Raider.objects.all()
    serializer_class = RaiderSerializer
    permission_classes = [IsAuthenticatedOrRead]

    def get_queryset(self):
        active = self.request.query_params.get("active")
        if active is not None:
            active = json.loads(
                active
            )  # converts javascript's 'true' to python's 'True'
            self.queryset = self.queryset.filter(active=active)

        name = self.request.query_params.get("name")
        if name is not None:
            self.queryset = self.queryset.filter(name=name)

        return self.queryset

    @action(detail=True, methods=["PUT"], url_path="calculate_experience")
    def calculate_experience_detail(self, request, pk=None):

        if pk is not None:
            raider = self.queryset.get(pk=pk)
            GenerateExperienceGainsForRaid.calculate_experience_for_raider(raider)

        return Response()

    @action(detail=False, methods=["PUT"], url_path="calculate_experience")
    def calculate_experience(self, request, pk=None):
        active = request.POST.get("active", None)

        GenerateExperienceGainsForRaid.calculate_experience_for_raiders(active)

        return Response()

class AliasesViewSet(viewsets.ModelViewSet):
    queryset = Alias.objects.all()
    serializer_class = AliasSerializer
    permission_classes = [IsAuthenticatedOrRead]
