from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from gxp.raids.models import Log, Raid
from gxp.raids.serializers import RaidSerializer, LogSerializer

from gxp.shared.warcraftLogs.interface import WarcraftLogsInterface
from gxp.shared.warcraftLogs.utils import WarcraftLogsUtils

class RaidsViewSet(viewsets.ModelViewSet):
    queryset = Raid.objects.all()
    serializer_class = RaidSerializer
    
class LogsViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer

    @action(detail=False, methods=['POST'])
    def pull(self, request):

        logs = WarcraftLogsInterface.get_logcodes_for_guild()
        new_logs_to_save= []
        for log in logs: 
            try:
                Log.objects.get(pk=log.get("code"))
            except Log.DoesNotExist:
                new_logs_to_save.append({
                    "logsCode": log.get("code"),
                    "zone": WarcraftLogsUtils.get_zone_name_from_report(log),
                    "timestamp": WarcraftLogsUtils.get_start_timestamp_from_report(log),
                })

        serailizer = LogSerializer(data=new_logs_to_save, many=True)
        serailizer.is_valid(raise_exception=True)
        serailizer.save()

        return Response(serailizer.data)
