"""Safe Query and Search Tools for ERPNext AI Agent."""

from typing import Any, Dict, List, Optional

from ERPNext_Agent.tools.base_tool import BaseTool


class SearchDocumentsTool(BaseTool):
	"""Tool to search documents with parameterized filters."""

	name = "search_documents"
	description = "Searches ERPNext documents matching criteria without using raw SQL."
	parameters_schema = {
		"type": "object",
		"properties": {
			"doctype": {"type": "string", "description": "Target DocType"},
			"filters": {"type": "object", "description": "Dictionary of filter criteria"},
			"fields": {
				"type": "array",
				"items": {"type": "string"},
				"description": "List of fields to fetch",
			},
			"limit": {"type": "integer", "description": "Maximum number of rows to return (default 20)"},
		},
		"required": ["doctype"],
	}

	def execute(
		self,
		doctype: str,
		filters: dict[str, Any] | None = None,
		fields: list[str] | None = None,
		limit: int = 20,
		**kwargs,
	) -> dict[str, Any]:
		self.validate_inputs({"doctype": doctype})
		return self.client.search_docs(doctype, filters=filters, fields=fields, limit=limit)


class GetValueTool(BaseTool):
	"""Tool to fetch specific field values of a single document."""

	name = "get_value"
	description = "Fetches specific field values directly from the database for quick read-back checks."
	parameters_schema = {
		"type": "object",
		"properties": {
			"doctype": {"type": "string", "description": "Target DocType"},
			"filters": {"type": "object", "description": "Dictionary of filters or document name"},
			"fieldname": {
				"type": "array",
				"items": {"type": "string"},
				"description": "Field or list of fields to fetch",
			},
		},
		"required": ["doctype", "filters", "fieldname"],
	}

	def execute(self, doctype: str, filters: Any, fieldname: Any, **kwargs) -> dict[str, Any]:
		self.validate_inputs({"doctype": doctype, "filters": filters, "fieldname": fieldname})
		return self.client.get_value(doctype=doctype, filters=filters, fieldname=fieldname)


class GetCountTool(BaseTool):
	"""Tool to count documents matching filters."""

	name = "get_count"
	description = "Returns the count of documents matching specified filters."
	parameters_schema = {
		"type": "object",
		"properties": {
			"doctype": {"type": "string", "description": "Target DocType"},
			"filters": {"type": "object", "description": "Dictionary of filter criteria"},
		},
		"required": ["doctype"],
	}

	def execute(self, doctype: str, filters: dict[str, Any] | None = None, **kwargs) -> dict[str, Any]:
		self.validate_inputs({"doctype": doctype})
		return self.client.get_count(doctype=doctype, filters=filters)
