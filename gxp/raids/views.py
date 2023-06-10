import logging

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from gxp.raids.models import Log, Raid
from gxp.raids.serializers import RaidSerializer, LogSerializer

from gxp.shared.warcraftLogs.interface import WarcraftLogsInterface
from gxp.shared.warcraftLogs.utils import WarcraftLogsUtils
from gxp.shared.permissions import IsAuthenticatedOrRead


class RaidsViewSet(viewsets.ModelViewSet):
    queryset = Raid.objects.all()
    serializer_class = RaidSerializer
    permission_classes = [IsAuthenticatedOrRead]


class LogsViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer
    permission_classes = [IsAuthenticatedOrRead]

    @action(detail=False, methods=["PUT"])
    def pull(self, request):
        logging.info("Pulling logs from warcraftlogs.com.")
        logs = WarcraftLogsInterface.get_logcodes_for_guild()
        new_logs_to_save = []
        for log in logs:
            try:
                Log.objects.get(pk=log.get("code"))
            except Log.DoesNotExist:
                logging.info(f"Saving new log {log.get('code')}")
                new_logs_to_save.append(
                    {
                        "logsCode": log.get("code"),
                        "zone": WarcraftLogsUtils.get_zone_name_from_report(log),
                        "timestamp": WarcraftLogsUtils.get_start_timestamp_from_report(
                            log
                        ),
                    }
                )

        serailizer = LogSerializer(data=new_logs_to_save, many=True)
        serailizer.is_valid(raise_exception=True)
        logging.info(f"Saving {len(new_logs_to_save)} new logs.")
        serailizer.save()

        return Response(serailizer.data)
