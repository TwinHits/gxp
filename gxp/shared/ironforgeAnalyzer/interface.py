from gxp.shared.api.api import Api
from gxp.shared.ironforgeAnalyzer.utils import IronforgeAnalyzerUtils

class IronforgeAnalyzerInterface:

    @staticmethod
    def get_consumes_for_report(report_id):
        try:
            response = Api.get(f"https://ironforge.pro/api/analyzer/{report_id}")
            return response.get("data")
        except Exception as err:
            IronforgeAnalyzerUtils.handle_error(err)
