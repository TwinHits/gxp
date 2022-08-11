from tkinter import W
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from gxp.raids.models import Raid
from gxp.raids.serializers import RaidSerializer
from gxp.shared.warcraftLogs.interface import WarcraftLogsInterface

class RaidsViewSet(viewsets.ModelViewSet):
    queryset = Raid.objects.all()
    serializer_class = RaidSerializer
    
class LogsView():

    @api_view(http_method_names=['GET'])
    def getLogs(request, format=None):
        raidLogIds = WarcraftLogsInterface.get_report_ids_for_guild()
        return Response(raidLogIds)
