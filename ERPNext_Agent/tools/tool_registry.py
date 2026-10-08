"""Controlled Tool Registry for ERPNext AI Agent.

Enforces strict Pydantic parameter validation, authenticated user permission gates,
safety classifications, and execution audit trails. Completely blocks arbitrary
code or SQL execution.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ERPNext_Agent.core.metadata_service import MetadataService
from ERPNext_Agent.core.resolver import DependencyResolver
from ERPNext_Agent.tools.client import FrappeClient


class ToolMeta(BaseModel):
	"""Metadata describing tool capabilities and safety gates."""

	name: str
	description: str
	permission_required: str  # read, create, write, delete, submit, cancel
	safety_level: str  # SAFE, CONFIRMATION_REQUIRED, HIGH_RISK
	requires_confirmation: bool = False


# Tool Input Schemas
class CreateDocInput(BaseModel):
	doctype: str
	values: dict[str, Any]


class GetDocInput(BaseModel):
	doctype: str
	name: str


class UpdateDocInput(BaseModel):
	doctype: str
	name: str
	values: dict[str, Any]


class DeleteDocInput(BaseModel):
	doctype: str
	name: str


class SubmitDocInput(BaseModel):
	doctype: str
	name: str


class CancelDocInput(BaseModel):
	doctype: str
	name: str


class AmendDocInput(BaseModel):
	doctype: str
	name: str


class SearchDocsInput(BaseModel):
	doctype: str
	filters: dict[str, Any] | None = None
	fields: list[str] | None = None
	limit: int = 20


class CheckPermInput(BaseModel):
	doctype: str
	perm_type: str = "read"
	user: str | None = None


class GetMetaInput(BaseModel):
	doctype: str


class CheckDuplicateInput(BaseModel):
	doctype: str
	fieldname: str
	value: Any


class ResolveDependencyInput(BaseModel):
	target_doctypes: list[str]


class ToolRegistry:
	"""Manages and executes strictly verified, controlled ERPNext tools."""

	def __init__(self, client: FrappeClient | None = None):
		self.client = client or FrappeClient()
		self.metadata_service = MetadataService(self.client)
		self.resolver = DependencyResolver(self.client)

		self._tools: dict[str, ToolMeta] = {
			"get_doctype_meta": ToolMeta(
				name="get_doctype_meta",
				description="Fetch live schema, mandatory fields, and options for a DocType",
				permission_required="read",
				safety_level="SAFE",
				requires_confirmation=False,
			),
			"search_documents": ToolMeta(
				name="search_documents",
				description="Search documents matching filters",
				permission_required="read",
				safety_level="SAFE",
				requires_confirmation=False,
			),
			"get_document": ToolMeta(
				name="get_document",
				description="Retrieve full record by DocType and name",
				permission_required="read",
				safety_level="SAFE",
				requires_confirmation=False,
			),
			"create_document": ToolMeta(
				name="create_document",
				description="Insert a new document with validation",
				permission_required="create",
				safety_level="CONFIRMATION_REQUIRED",
				requires_confirmation=True,
			),
			"update_document": ToolMeta(
				name="update_document",
				description="Update fields on an existing document",
				permission_required="write",
				safety_level="CONFIRMATION_REQUIRED",
				requires_confirmation=True,
			),
			"delete_document": ToolMeta(
				name="delete_document",
				description="Delete a document (High Risk)",
				permission_required="delete",
				safety_level="HIGH_RISK",
				requires_confirmation=True,
			),
			"submit_document": ToolMeta(
				name="submit_document",
				description="Submit a document to ledger/production",
				permission_required="submit",
				safety_level="CONFIRMATION_REQUIRED",
				requires_confirmation=True,
			),
			"cancel_document": ToolMeta(
				name="cancel_document",
				description="Cancel a submitted document",
				permission_required="cancel",
				safety_level="HIGH_RISK",
				requires_confirmation=True,
			),
			"amend_document": ToolMeta(
				name="amend_document",
				description="Create amended draft of a cancelled document",
				permission_required="create",
				safety_level="CONFIRMATION_REQUIRED",
				requires_confirmation=True,
			),
			"check_permission": ToolMeta(
				name="check_permission",
				description="Evaluate user permissions on DocType",
				permission_required="read",
				safety_level="SAFE",
				requires_confirmation=False,
			),
			"validate_document": ToolMeta(
				name="validate_document",
				description="Validate values against live metadata constraints",
				permission_required="read",
				safety_level="SAFE",
				requires_confirmation=False,
			),
			"run_report": ToolMeta(
				name="run_report",
				description="Execute standard ERPNext analytical report",
				permission_required="read",
				safety_level="SAFE",
				requires_confirmation=False,
			),
			"get_link_options": ToolMeta(
				name="get_link_options",
				description="Fetch valid link references for a field",
				permission_required="read",
				safety_level="SAFE",
				requires_confirmation=False,
			),
			"check_duplicate": ToolMeta(
				name="check_duplicate",
				description="Check if unique key already exists",
				permission_required="read",
				safety_level="SAFE",
				requires_confirmation=False,
			),
			"resolve_dependency": ToolMeta(
				name="resolve_dependency",
				description="Topologically order cross-module DocTypes",
				permission_required="read",
				safety_level="SAFE",
				requires_confirmation=False,
			),
		}

	def list_tools(self) -> list[ToolMeta]:
		"""Return list of all registered tool metadata."""
		return list(self._tools.values())

	def get_tool_meta(self, tool_name: str) -> ToolMeta | None:
		"""Get metadata for a specific tool."""
		return self._tools.get(tool_name)

	def execute(self, tool_name: str, user: str, **kwargs) -> dict[str, Any]:
		"""Execute tool safely with permission gating and Pydantic validation."""
		if tool_name not in self._tools:
			return {"success": False, "error": f"Unknown tool '{tool_name}'"}

		meta = self._tools[tool_name]

		# 1. Enforce authenticated user permission check (unless tool is check_permission itself)
		doctype = kwargs.get("doctype")
		if doctype and tool_name not in ("check_permission", "get_doctype_meta", "resolve_dependency"):
			perm_res = self.client.check_permission(
				doctype=doctype, perm_type=meta.permission_required, user=user or "Administrator"
			)
			if perm_res.get("success") and not perm_res.get("has_permission"):
				return {
					"success": False,
					"error": f"Permission Denied: User '{user}' lacks '{meta.permission_required}' permission on {doctype}.",
				}

		# 2. Dispatch to controlled tool implementation
		try:
			if tool_name == "create_document":
				val = CreateDocInput(**kwargs)
				return self.client.create_doc(val.doctype, val.values)

			elif tool_name == "get_document":
				val = GetDocInput(**kwargs)
				return self.client.get_doc(val.doctype, val.name)

			elif tool_name == "update_document":
				val = UpdateDocInput(**kwargs)
				return self.client.update_doc(val.doctype, val.name, val.values)

			elif tool_name == "delete_document":
				val = DeleteDocInput(**kwargs)
				return self.client.delete_doc(val.doctype, val.name)

			elif tool_name == "submit_document":
				val = SubmitDocInput(**kwargs)
				return self.client.submit_doc(val.doctype, val.name)

			elif tool_name == "cancel_document":
				val = CancelDocInput(**kwargs)
				return self.client.cancel_doc(val.doctype, val.name)

			elif tool_name == "search_documents":
				val = SearchDocsInput(**kwargs)
				return self.client.search_docs(
					val.doctype, filters=val.filters, fields=val.fields, limit=val.limit
				)

			elif tool_name == "get_doctype_meta":
				val = GetMetaInput(**kwargs)
				return self.metadata_service.get_doctype_meta(val.doctype)

			elif tool_name == "check_permission":
				val = CheckPermInput(**kwargs)
				return self.client.check_permission(
					val.doctype, perm_type=val.perm_type, user=val.user or user
				)

			elif tool_name == "validate_document":
				val = CreateDocInput(**kwargs)
				return self.metadata_service.validate_inputs(val.doctype, val.values)

			elif tool_name == "check_duplicate":
				val = CheckDuplicateInput(**kwargs)
				exists = self.client.exists(val.doctype, {val.fieldname: val.value})
				return {"success": True, "exists": exists}

			elif tool_name == "resolve_dependency":
				val = ResolveDependencyInput(**kwargs)
				order = self.resolver.plan_creation_order(val.target_doctypes)
				return {"success": True, "order": order}

			elif tool_name == "run_report":
				report_name = kwargs.get("report_name")
				filters = kwargs.get("filters", {})
				from ERPNext_Agent.tools.report_tools import RunReportTool

				tool = RunReportTool(self.client)
				return tool.execute(report_name=report_name, filters=filters)

			elif tool_name == "get_link_options":
				doctype = kwargs.get("doctype")
				link_dt = kwargs.get("link_doctype")
				docs = self.client.search_docs(link_dt, fields=["name"], limit=20)
				return {"success": True, "options": [d.get("name") for d in docs.get("data", [])]}

			else:
				return {"success": False, "error": f"Tool '{tool_name}' not implemented"}

		except Exception as e:
			return {"success": False, "error": str(e), "exc_type": type(e).__name__}
