from sarathi_visibility.api.dashboard import REPORTS, report_data
from sarathi_visibility.api.dashboard_data import load


def execute(filters=None):
    filters = filters or {}
    data = load(filters)
    report = filters.get("report_type") or "projects"
    report = next((key for key, definition in REPORTS.items() if definition[0] == report), report)
    result = report_data(data, report, filters.get("subset") or "", filters.get("search") or "")
    return REPORTS[report][2], result, "Dates filter transactional activity. Project status, BOMs, operation balances, production summaries and semi-finished stock are current; operation balances cover lifetime submitted Work Orders.", None, [{"label": "Matching records", "value": len(result), "datatype": "Int"}]
