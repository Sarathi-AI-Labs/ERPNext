"""Live ERPNext Metadata Service.

Provides the dynamic runtime source of truth for all DocType schemas using frappe.get_meta().
Discovers mandatory fields, field types, link targets, select options, defaults, child tables,
and permissions dynamically at runtime instead of relying on hardcoded slot definitions.
"""

from typing import Any, Dict, List, Optional

from ERPNext_Agent.tools.client import FrappeClient


class MetadataService:
	"""Dynamic schema discovery and inspection service backed by live Frappe metadata."""

	def __init__(self, client: FrappeClient | None = None):
		self.client = client or FrappeClient()
		self._meta_cache: dict[str, dict[str, Any]] = {}
		self._link_options_cache: dict[str, list[str]] = {}

	def clear_cache(self, doctype: str | None = None):
		"""Invalidate metadata cache for immediate live synchronization."""
		if doctype:
			self._meta_cache.pop(doctype.strip(), None)
		else:
			self._meta_cache.clear()
			self._link_options_cache.clear()

	def get_link_options(self, target_doctype: str, limit: int = 100) -> list[str]:
		"""Fetch and cache live Link target options directly from Frappe runtime."""
		if not target_doctype:
			return []
		if target_doctype in self._link_options_cache:
			return self._link_options_cache[target_doctype]
		opts = self.client.get_link_options(target_doctype, limit=limit)
		if opts:
			self._link_options_cache[target_doctype] = opts
		return opts

	def get_doctype_meta(self, doctype: str) -> dict[str, Any]:
		"""Fetch and structure live metadata from Frappe."""
		dt_clean = doctype.strip()
		if dt_clean in self._meta_cache:
			return self._meta_cache[dt_clean]

		res = self.client.get_meta(dt_clean)
		if not res.get("success"):
			return {
				"success": False,
				"doctype": dt_clean,
				"error": res.get("error", f"Could not retrieve metadata for DocType {dt_clean}"),
			}

		fields_raw = res.get("fields", [])
		mandatory_fields = []
		field_map = {}
		link_fields = {}
		select_options = {}
		child_tables = {}
		defaults = {}

		for f in fields_raw:
			fname = f.get("fieldname")
			ftype = f.get("fieldtype")
			label = f.get("label") or fname
			reqd = bool(f.get("reqd"))
			read_only = bool(f.get("read_only"))
			default_val = f.get("default")
			options = f.get("options")

			field_info = {
				"fieldname": fname,
				"label": label,
				"fieldtype": ftype,
				"reqd": reqd,
				"read_only": read_only,
				"default": default_val,
				"options": options,
			}
			field_map[fname] = field_info

			# Collect mandatory editable fields
			if reqd and not read_only:
				mandatory_fields.append(
					{
						"fieldname": fname,
						"label": label,
						"fieldtype": ftype,
						"options": options,
						"default": default_val,
					}
				)

			if ftype == "Link" and options:
				link_fields[fname] = options
			elif ftype == "Select" and options:
				select_options[fname] = [opt.strip() for opt in str(options).splitlines() if opt.strip()]
			elif ftype == "Table" and options:
				child_tables[fname] = options

			if default_val:
				defaults[fname] = default_val

		meta_structured = {
			"success": True,
			"doctype": dt_clean,
			"module": res.get("module") or "General",
			"is_submittable": res.get("is_submittable", False),
			"autoname": res.get("autoname"),
			"fields": field_map,
			"fields_list": fields_raw,
			"mandatory_fields": mandatory_fields,
			"link_fields": link_fields,
			"select_options": select_options,
			"child_tables": child_tables,
			"defaults": defaults,
		}

		self._meta_cache[dt_clean] = meta_structured
		return meta_structured

	def get_mandatory_fields(self, doctype: str) -> list[dict[str, Any]]:
		"""Return list of mandatory user-input fields for a DocType."""
		meta = self.get_doctype_meta(doctype)
		return meta.get("mandatory_fields", [])

	def get_defaults(self, doctype: str) -> dict[str, Any]:
		"""Return dictionary of default field values from live schema."""
		meta = self.get_doctype_meta(doctype)
		return meta.get("defaults", {})

	def validate_inputs(self, doctype: str, values: dict[str, Any]) -> dict[str, Any]:
		"""Validate input values against live Frappe metadata constraints."""
		meta = self.get_doctype_meta(doctype)
		if not meta.get("success"):
			return {"valid": False, "missing": [], "errors": [meta.get("error")]}

		missing = []
		errors = []

		# 1. Check mandatory fields
		for mf in meta.get("mandatory_fields", []):
			fname = mf["fieldname"]
			if fname not in values or values[fname] is None or values[fname] == "":
				missing.append(mf)

		# 2. Check Select options
		select_opts = meta.get("select_options", {})
		for fname, opts in select_opts.items():
			if fname in values and values[fname] and opts:
				val = str(values[fname]).strip()
				if val not in opts and val.lower() not in [o.lower() for o in opts]:
					errors.append(f"Invalid option '{val}' for field '{fname}'. Allowed: {opts}")

		return {"valid": len(missing) == 0 and len(errors) == 0, "missing": missing, "errors": errors}
