import json
from typing import Any, Dict

from ERPNext_Agent.tools.base_tool import BaseTool


class SubmitDocumentTool(BaseTool):
	"""Tool to submit a submittable document (docstatus 0 -> 1)."""

	name = "submit_document"
	description = "Submits a submittable ERPNext document, transitioning it from Draft (0) to Submitted (1)."
	parameters_schema = {
		"type": "object",
		"properties": {
			"doctype": {"type": "string", "description": "DocType name"},
			"name": {"type": "string", "description": "Document Name / ID"},
		},
		"required": ["doctype", "name"],
	}

	def execute(self, doctype: str, name: str, **kwargs) -> dict[str, Any]:
		self.validate_inputs({"doctype": doctype, "name": name})
		return self.client.submit_doc(doctype, name)


class CancelDocumentTool(BaseTool):
	"""Tool to cancel a submitted document (docstatus 1 -> 2)."""

	name = "cancel_document"
	description = (
		"Cancels a submitted ERPNext document, transitioning it from Submitted (1) to Cancelled (2)."
	)
	parameters_schema = {
		"type": "object",
		"properties": {
			"doctype": {"type": "string", "description": "DocType name"},
			"name": {"type": "string", "description": "Document Name / ID"},
		},
		"required": ["doctype", "name"],
	}

	def execute(self, doctype: str, name: str, **kwargs) -> dict[str, Any]:
		self.validate_inputs({"doctype": doctype, "name": name})
		return self.client.cancel_doc(doctype, name)


class AmendDocumentTool(BaseTool):
	"""Tool to amend a cancelled document."""

	name = "amend_document"
	description = "Creates a new draft amended copy from a cancelled document."
	parameters_schema = {
		"type": "object",
		"properties": {
			"doctype": {"type": "string", "description": "DocType name"},
			"name": {"type": "string", "description": "Name of cancelled document to amend"},
		},
		"required": ["doctype", "name"],
	}

	def execute(self, doctype: str, name: str, **kwargs) -> dict[str, Any]:
		self.validate_inputs({"doctype": doctype, "name": name})
		code = f"""
    cancelled_doc = frappe.get_doc({json.dumps(doctype)}, {json.dumps(name)})
    if cancelled_doc.docstatus != 2:
        print(json.dumps({{'success': False, 'error': f"Only cancelled documents can be amended. Current docstatus: {{cancelled_doc.docstatus}}"}}))
    else:
        amended = frappe.copy_doc(cancelled_doc)
        amended.amended_from = {json.dumps(name)}
        amended.docstatus = 0
        amended.insert()
        frappe.db.commit()
        print(json.dumps({{'success': True, 'doctype': {json.dumps(doctype)}, 'name': amended.name, 'data': amended.as_dict()}}, default=str))
"""
		return self.client.execute_script(code)
