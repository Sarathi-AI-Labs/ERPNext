"""Native, session-bound client for the existing conversational agent.

The external agent package remains untouched. Its unrestricted read/IPC helpers
are deliberately not used from a dashboard session.
"""

import frappe
from frappe.model.workflow import get_workflow_name

from ERPNext_Agent.tools.client import FrappeClient
from sarathi_visibility.api.access import (
	FINANCIAL_DOCTYPES,
	MONEY_FIELDS,
	allowed_fields,
	can_finance,
	check_record,
	deny,
	require_capability,
	scoped_count,
	scoped_rows,
	scoped_value,
)

PROTECTED_FIELDS = {
	"name",
	"doctype",
	"owner",
	"creation",
	"modified",
	"modified_by",
	"docstatus",
	"workflow_state",
	"status",
}


class DashboardAgentClient(FrappeClient):
	def execute_script(self, python_code):
		# No privileged IPC or arbitrary script execution from a web request.
		deny()

	def _source(self, doctype):
		require_capability("production")
		if doctype in FINANCIAL_DOCTYPES and not can_finance():
			deny()

	def _data(self, doc):
		doc.apply_fieldlevel_read_permissions()
		permitted = allowed_fields(doc.doctype) | {"doctype"}
		result = {k: v for k, v in doc.as_dict().items() if k in permitted}
		for field in doc.meta.fields:
			if field.fieldtype in ("Table", "Table MultiSelect") and field.fieldname in result:
				fields = allowed_fields(field.options) | {"doctype"}
				result[field.fieldname] = [
					{k: v for k, v in r.items() if k in fields} for r in result[field.fieldname]
				]
		return result

	def _filters(self, doctype, filters):
		if not filters:
			return filters
		permitted = allowed_fields(doctype)
		if isinstance(filters, dict):
			fields = list(filters)
		elif isinstance(filters, (list, tuple)):
			fields = []
			for row in filters:
				if not isinstance(row, (list, tuple)) or len(row) not in (3, 4):
					deny()
				if len(row) == 4 and row[0] != doctype:
					deny()
				fields.append(row[-3])
		else:
			deny()
		if len(fields) > 20 or any(f not in permitted for f in fields):
			deny()
		return filters

	def get_doc(self, doctype, name):
		self._source(doctype)
		doc = check_record(doctype, name)
		return {"success": True, "doctype": doctype, "name": name, "data": self._data(doc)}

	def search_docs(self, doctype, filters=None, fields=None, limit=20):
		self._source(doctype)
		data = scoped_rows(
			doctype,
			filters=self._filters(doctype, filters),
			fields=fields or ["name"],
			limit_page_length=min(max(int(limit), 1), 100),
		)
		return {"success": True, "doctype": doctype, "count": len(data), "data": data}

	def get_link_options(self, target_doctype, limit=100):
		self._source(target_doctype)
		return scoped_rows(target_doctype, pluck="name", limit_page_length=min(max(int(limit), 1), 100))

	def get_value(self, doctype, filters, fieldname):
		self._source(doctype)
		value = scoped_value(doctype, self._filters(doctype, filters), fieldname, as_dict=True)
		return {"success": value is not None, "doctype": doctype, "data": value}

	def get_count(self, doctype, filters=None):
		self._source(doctype)
		return {
			"success": True,
			"doctype": doctype,
			"count": scoped_count(doctype, self._filters(doctype, filters)),
		}

	def exists(self, doctype, filters):
		self._source(doctype)
		return bool(scoped_value(doctype, self._filters(doctype, filters), "name"))

	def check_permission(self, doctype, perm_type="read", user=None, doc=None):
		self._source(doctype)
		# Never honor a client/graph supplied Administrator identity.
		target = check_record(doctype, doc) if doc else None
		allowed = frappe.has_permission(doctype, perm_type, doc=target, user=frappe.session.user)
		return {"success": True, "allowed": bool(allowed), "has_permission": bool(allowed)}

	def get_meta(self, doctype):
		self._source(doctype)
		if not (frappe.has_permission(doctype, "read") or frappe.has_permission(doctype, "create")):
			deny()
		result = super().get_meta(doctype)
		permitted = allowed_fields(doctype)
		result["fields"] = [f for f in result.get("fields", []) if f["fieldname"] in permitted]
		return result

	def _write(self, doctype, name, operation, values=None):
		self._source(doctype)
		if operation == "create":
			if not frappe.has_permission(doctype, "create"):
				deny()
			doc = frappe.new_doc(doctype)
		else:
			doc = check_record(doctype, name, operation if operation != "update" else "write")
		if get_workflow_name(doctype):
			frappe.throw("Use the authorized ERPNext workflow for this document.")
		if operation in ("create", "update"):
			if not isinstance(values, dict) or set(values) & PROTECTED_FIELDS:
				frappe.throw("Unsupported dashboard changes.")
			if any(
				doc.meta.get_field(k) and doc.meta.get_field(k).fieldtype in ("Table", "Table MultiSelect")
				for k in values
			):
				frappe.throw("Edit child rows through the authorized ERPNext form.")
			if any(
				doc.meta.get_field(k) and doc.meta.get_field(k).fieldtype in ("Table", "Table MultiSelect")
				for k in values
			):
				frappe.throw("Edit child rows through the authorized ERPNext form.")
			levels = doc.meta.get_permlevel_access(permission_type="write", user=frappe.session.user)
			for key in values:
				f = doc.meta.get_field(key)
				if (
					not f
					or f.read_only
					or (f.permlevel or 0) not in levels
					or (not can_finance() and (f.fieldtype == "Currency" or key in MONEY_FIELDS))
				):
					deny()
			if operation == "update" and doc.docstatus != 0:
				frappe.throw("Submitted documents cannot be edited here.")
			doc.update(values)
			doc.insert() if operation == "create" else doc.save()
		elif operation == "submit":
			if doc.docstatus != 0:
				frappe.throw("Only a draft can be submitted.")
			doc.submit()
		elif operation == "cancel":
			if doc.docstatus != 1:
				frappe.throw("Only a submitted document can be cancelled.")
			doc.cancel()
		elif operation == "delete":
			if doc.docstatus != 0:
				frappe.throw("Only a draft can be deleted here.")
			frappe.delete_doc(doctype, name)
		return {"success": True, "doctype": doctype, "name": doc.name}

	def create_doc(self, doctype, values):
		return self._write(doctype, None, "create", values)

	def update_doc(self, doctype, name, values):
		return self._write(doctype, name, "update", values)

	def submit_doc(self, doctype, name):
		return self._write(doctype, name, "submit")

	def cancel_doc(self, doctype, name):
		return self._write(doctype, name, "cancel")

	def delete_doc(self, doctype, name):
		return self._write(doctype, name, "delete")
