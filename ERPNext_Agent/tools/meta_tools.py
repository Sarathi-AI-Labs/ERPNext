"""Meta & Permission Tools for ERPNext AI Agent."""

from typing import Any, Dict

from ERPNext_Agent.tools.base_tool import BaseTool


class GetDocMetaTool(BaseTool):
	"""Tool to inspect metadata, field definitions, and submittability of any DocType."""

	name = "get_doc_meta"
	description = "Retrieves live DocType metadata, field definitions, mandatory rules, and submittability."
	parameters_schema = {
		"type": "object",
		"properties": {"doctype": {"type": "string", "description": "Target DocType name"}},
		"required": ["doctype"],
	}

	def execute(self, doctype: str, **kwargs) -> dict[str, Any]:
		self.validate_inputs({"doctype": doctype})
		return self.client.get_meta(doctype)


class CheckPermissionTool(BaseTool):
	"""Tool to check user permissions (read, write, create, submit, cancel) on a DocType."""

	name = "check_permission"
	description = (
		"Checks whether a specified user has permission (read, write, create, submit, cancel) on a DocType."
	)
	parameters_schema = {
		"type": "object",
		"properties": {
			"doctype": {"type": "string", "description": "Target DocType"},
			"perm_type": {
				"type": "string",
				"enum": ["read", "write", "create", "submit", "cancel", "delete"],
				"description": "Permission action to test (default 'read')",
			},
			"user": {"type": "string", "description": "Frappe user email (default 'Administrator')"},
			"doc": {"type": "string", "description": "Optional specific document name"},
		},
		"required": ["doctype"],
	}

	def execute(
		self, doctype: str, perm_type: str = "read", user: str = "Administrator", doc: str = None, **kwargs
	) -> dict[str, Any]:
		self.validate_inputs({"doctype": doctype})
		return self.client.check_permission(doctype, perm_type=perm_type, user=user, doc=doc)
