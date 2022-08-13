from gxp.shared.api.api import Api

from gxp.shared.raidHelper.utils import RaidHelperUtils

class RaidHelperInterface:

    @staticmethod
    def get_sign_ups_for_event_id(event_id):
        try:
            response = Api.get(f"https://raid-helper.dev/api/event/{event_id}")
            return response
        except Exception as err:
            RaidHelperUtils.handle_error(err)
