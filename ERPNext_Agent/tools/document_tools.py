"""Document CRUD Tools for ERPNext AI Agent."""

from typing import Any, Dict

from ERPNext_Agent.tools.base_tool import BaseTool


class CreateDocumentTool(BaseTool):
	"""Tool to create a new document in Frappe/ERPNext."""

	name = "create_document"
	description = "Creates a new document of specified DocType with provided field values."
	parameters_schema = {
		"type": "object",
		"properties": {
			"doctype": {
				"type": "string",
				"description": "Target ERPNext DocType (e.g. 'Company', 'Item', 'BOM')",
			},
			"values": {"type": "object", "description": "Dictionary of field name and value pairs"},
		},
		"required": ["doctype", "values"],
	}

	def execute(self, doctype: str, values: dict[str, Any], **kwargs) -> dict[str, Any]:
		self.validate_inputs({"doctype": doctype, "values": values})
		return self.client.create_doc(doctype, values)


class GetDocumentTool(BaseTool):
	"""Tool to fetch an existing document from Frappe/ERPNext."""

	name = "get_document"
	description = "Fetches a full document by DocType and Name including child tables."
	parameters_schema = {
		"type": "object",
		"properties": {
			"doctype": {"type": "string", "description": "DocType name"},
			"name": {"type": "string", "description": "Document ID or Name"},
		},
		"required": ["doctype", "name"],
	}

	def execute(self, doctype: str, name: str, **kwargs) -> dict[str, Any]:
		self.validate_inputs({"doctype": doctype, "name": name})
		return self.client.get_doc(doctype, name)


class UpdateDocumentTool(BaseTool):
	"""Tool to update an existing document in Frappe/ERPNext."""

	name = "update_document"
	description = "Updates fields of an existing document by DocType and Name."
	parameters_schema = {
		"type": "object",
		"properties": {
			"doctype": {"type": "string", "description": "DocType name"},
			"name": {"type": "string", "description": "Document ID or Name"},
			"values": {"type": "object", "description": "Fields to update with new values"},
		},
		"required": ["doctype", "name", "values"],
	}

	def execute(self, doctype: str, name: str, values: dict[str, Any], **kwargs) -> dict[str, Any]:
		self.validate_inputs({"doctype": doctype, "name": name, "values": values})
		return self.client.update_doc(doctype, name, values)


class DeleteDocumentTool(BaseTool):
	"""Tool to delete an existing document in Frappe/ERPNext."""

	name = "delete_document"
	description = "Deletes a draft or cancelled document by DocType and Name."
	parameters_schema = {
		"type": "object",
		"properties": {
			"doctype": {"type": "string", "description": "DocType name"},
			"name": {"type": "string", "description": "Document ID or Name"},
		},
		"required": ["doctype", "name"],
	}

	def execute(self, doctype: str, name: str, **kwargs) -> dict[str, Any]:
		self.validate_inputs({"doctype": doctype, "name": name})
		return self.client.delete_doc(doctype, name)
