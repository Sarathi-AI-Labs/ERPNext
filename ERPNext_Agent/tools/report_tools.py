"""Report Execution Tool for ERPNext AI Agent."""

import json
from typing import Any, Dict, Optional

from ERPNext_Agent.tools.base_tool import BaseTool


class RunReportTool(BaseTool):
	"""Tool to execute standard Frappe & ERPNext reports safely."""

	name = "run_report"
	description = "Executes an ERPNext or Frappe report (Query Report or Script Report) safely and returns tabular data."
	parameters_schema = {
		"type": "object",
		"properties": {
			"report_name": {"type": "string", "description": "Exact name of Report DocType"},
			"filters": {"type": "object", "description": "Key-value dictionary of report filters"},
			"user": {"type": "string", "description": "User context for execution (default 'Administrator')"},
		},
		"required": ["report_name"],
	}

	def execute(
		self, report_name: str, filters: dict[str, Any] | None = None, user: str = "Administrator", **kwargs
	) -> dict[str, Any]:
		self.validate_inputs({"report_name": report_name})
		code = f"""
    from frappe.desk.query_report import run
    flt = {json.dumps(filters or {})}
    res = run(report_name={json.dumps(report_name)}, filters=flt, user={json.dumps(user)})
    # Trim large results to avoid memory spikes
    columns = res.get('columns', [])
    data = res.get('result', [])
    trimmed_data = data[:100] if isinstance(data, list) else data
    print(json.dumps({{'success': True, 'report_name': {json.dumps(report_name)}, 'total_rows': len(data) if isinstance(data, list) else 0, 'columns': columns, 'result': trimmed_data}}, default=str))
"""
		return self.client.execute_script(code)
