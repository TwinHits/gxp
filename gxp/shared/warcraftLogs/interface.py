from django.conf import settings

import base64
import json

from gxp.shared.api.api import Api
from gxp.shared.warcraftLogs.queries import Queries

class WarcraftLogsInterface:

    client_id = settings.WARCRAFT_LOGS_CLIENT_ID
    client_secret = settings.WARCRAFT_LOGS_CLIENT_SECRET

    base_url = settings.WARCRAFT_LOGS_BASE_URL
    authorize_url = base_url + settings.WARCRAFT_LOGS_AUTHORIZE_ENDPOINT
    token_url = base_url + settings.WARCRAFT_LOGS_TOKEN_ENDPOINT
    endpoint = base_url + "/api/v2/client"


    @staticmethod
    def get_message_from_errors(dict):
        message = ""
        errors = dict.get("errors") 
        for error in errors:
            message += error.get("message") + " "
        return message
        

    @staticmethod
    def authenticate():
        client_credentials_encoded = f"{WarcraftLogsInterface.client_id}:{WarcraftLogsInterface.client_secret}".encode("utf-8")
        authorization_header_value =  f'Basic {base64.b64encode(client_credentials_encoded).decode("utf-8")}'
        body = "grant_type=client_credentials"
        response = Api.post(WarcraftLogsInterface.token_url, data=body, headers={
                'Authorization': authorization_header_value,
                'Content-Type': 'application/x-www-form-urlencoded',
            })
        return response


    @staticmethod
    def get_raids_for_guild():
        auth = WarcraftLogsInterface.authenticate()
        body = {
            "query": Queries.GET_RAIDS_BY_GUILD_ID,
            "variables":  { 
                "page": 0
            }
        };

        response = Api.post(WarcraftLogsInterface.endpoint, json=body, headers={
            "Authorization": f'Bearer {auth.get("access_token")}',
            'Content-Type': 'application/json',
        })

        if response.get("errors"):
            raise Exception(WarcraftLogsInterface.get_message_from_errors(response))


    @staticmethod
    def get_raid_by_report_id(reportId):
        auth = WarcraftLogsInterface.authenticate()
        body = {
            "query": Queries.GET_RAID_BY_REPORT_ID,
            "variables":  { 
                "code": reportId
            }
        };

        response = Api.post(WarcraftLogsInterface.endpoint, json=body, headers={
            "Authorization": f'Bearer {auth.get("access_token")}',
            'Content-Type': 'application/json',
        })

        if response.get("errors"):
            raise Exception(WarcraftLogsInterface.get_message_from_errors(response))

