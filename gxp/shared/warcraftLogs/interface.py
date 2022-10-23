from django.conf import settings

import base64

from gxp.shared.api.api import Api
from gxp.shared.warcraftLogs.queries import Queries
from gxp.shared.warcraftLogs.utils import WarcraftLogsUtils


class WarcraftLogsInterface:

    client_id = settings.WARCRAFT_LOGS_CLIENT_ID
    client_secret = settings.WARCRAFT_LOGS_CLIENT_SECRET

    base_url = settings.WARCRAFT_LOGS_BASE_URL
    authorize_url = base_url + settings.WARCRAFT_LOGS_AUTHORIZE_ENDPOINT
    token_url = base_url + settings.WARCRAFT_LOGS_TOKEN_ENDPOINT
    endpoint = base_url + "/api/v2/client"

    @staticmethod
    def authenticate():
        client_credentials_encoded = f"{WarcraftLogsInterface.client_id}:{WarcraftLogsInterface.client_secret}".encode(
            "utf-8"
        )
        authorization_header_value = (
            f'Basic {base64.b64encode(client_credentials_encoded).decode("utf-8")}'
        )
        body = "grant_type=client_credentials"
        response = Api.post(
            WarcraftLogsInterface.token_url,
            data=body,
            headers={
                "Authorization": authorization_header_value,
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        return response

    @staticmethod
    def __post_grapql_query(query, variables):
        auth = WarcraftLogsInterface.authenticate()
        body = {
            "query": query,
            "variables": variables,
        }

        response = Api.post(
            WarcraftLogsInterface.endpoint,
            json=body,
            headers={
                "Authorization": f'Bearer {auth.get("access_token")}',
                "Content-Type": "application/json",
            },
        )

        if response.get("errors"):
            raise Exception(WarcraftLogsUtils.get_message_from_errors(response))

        return response

    @staticmethod
    def get_logcodes_for_guild():
        log_codes = []
        page = 1
        has_more_pages = True
        while has_more_pages:
            response = WarcraftLogsInterface.__post_grapql_query(
                Queries.GET_REPORTS_BY_GUILD, {"page": page}
            )
            log_codes.extend(
                response.get("data")
                .get("guildData")
                .get("guild")
                .get("attendance")
                .get("data")
            )
            has_more_pages = (
                response.get("data")
                .get("guildData")
                .get("guild")
                .get("attendance")
                .get("has_more_pages")
            )
            page += 1
        return log_codes

    @staticmethod
    def get_raiders_and_encounters_by_report_id(reportId):
        report = WarcraftLogsInterface.get_raid_by_report_id(reportId)
        raiders = WarcraftLogsUtils.get_or_create_raiders_from_report(report)
        encounters = WarcraftLogsUtils.get_number_of_enocunters_from_report(report)
        return raiders, encounters

    @staticmethod
    def get_raid_by_report_id(reportId):
        response = WarcraftLogsInterface.__post_grapql_query(
            Queries.GET_RAID_BY_REPORT_ID, {"code": reportId}
        )
        return response.get("data").get("reportData").get("report")

    @staticmethod
    def get_raid_kills_by_report_id(reportId):
        response = WarcraftLogsInterface.__post_grapql_query(
            Queries.GET_RAID_KILLS_BY_REPORT_ID, {"code": reportId}
        )
        return response.get("data").get("reportData").get("report")

    @staticmethod
    def get_performance_by_report_id(reportId, type):
        
        if type == 'hps':
            query = Queries.GET_PERFORMANCE_BY_REPORT_ID_HPS
        elif type == 'dps':
            query = Queries.GET_PERFORMANCE_BY_REPORT_ID_DPS

        response = WarcraftLogsInterface.__post_grapql_query(
            query, {"code": reportId}
        )
        return response.get("data").get("reportData").get("report")
