"""Frappe Client Interface for ERPNext AI Agent.

Executes atomic, parameterized operations against Frappe / ERPNext either
natively (when running inside the Frappe bench process) or via containerized
IPC bridge (when running externally on host) with zero arbitrary SQL or shell injections.
"""

import json
import subprocess
from typing import Any, Dict, List, Optional


class FrappeClient:
	"""Hybrid Native/IPC Bridge to Frappe Framework & ERPNext."""

	def __init__(self, container_name: str = "frappe_docker_main-backend-1", site_name: str = "frontend"):
		self.container_name = container_name
		self.site_name = site_name

	def _is_native_frappe(self) -> bool:
		"""Check if executing inside an active Frappe bench environment."""
		try:
			import frappe

			return bool(hasattr(frappe, "db") and frappe.db)
		except (ImportError, Exception):
			return False

	def execute_script(self, python_code: str) -> dict[str, Any]:
		"""Execute a Python snippet inside Frappe environment and parse JSON response."""
		if self._is_native_frappe():
			import io
			import sys

			import frappe

			# Capture print outputs in a safe scope
			old_stdout = sys.stdout
			redirected_output = io.StringIO()
			sys.stdout = redirected_output
			try:
				local_scope = {"frappe": frappe, "json": json, "sys": sys}
				exec(python_code, local_scope)
				output = redirected_output.getvalue().strip()
				for line in reversed(output.splitlines()):
					line = line.strip()
					if line.startswith("{") and line.endswith("}"):
						try:
							return json.loads(line)
						except json.JSONDecodeError:
							continue
				return {"success": True, "output": output}
			except Exception as e:
				frappe.db.rollback()
				return {"success": False, "error": str(e), "exc_type": type(e).__name__}
			finally:
				sys.stdout = old_stdout

		wrapper = f"""
import json, sys, frappe
try:
    frappe.init('{self.site_name}')
    frappe.connect()
{python_code}
except Exception as e:
    frappe.db.rollback()
    print(json.dumps({{'success': False, 'error': str(e), 'exc_type': type(e).__name__}}))
    sys.exit(0)
finally:
    try:
        frappe.destroy()
    except Exception:
        pass
"""
		cmd = [
			"docker",
			"exec",
			"-i",
			"-w",
			"/home/frappe/frappe-bench/sites",
			self.container_name,
			"/home/frappe/frappe-bench/env/bin/python",
			"-c",
			wrapper,
		]
		try:
			proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
			stdout = proc.stdout.strip()
			stderr = proc.stderr.strip()
			if proc.returncode != 0 and not stdout:
				return {"success": False, "error": stderr or f"Process exited with code {proc.returncode}"}

			# Find the last JSON output line
			for line in reversed(stdout.splitlines()):
				line = line.strip()
				if line.startswith("{") and line.endswith("}"):
					try:
						return json.loads(line)
					except json.JSONDecodeError:
						continue

			return {"success": False, "error": f"Invalid response from Frappe: {stdout}\n{stderr}"}
		except subprocess.TimeoutExpired:
			return {"success": False, "error": "Operation timed out after 60 seconds."}
		except Exception as e:
			return {"success": False, "error": str(e)}

	def create_doc(self, doctype: str, values: dict[str, Any]) -> dict[str, Any]:
		"""Create a new document in Frappe with validation."""
		if self._is_native_frappe():
			import frappe

			try:
				doc = frappe.new_doc(doctype)
				doc.update(values)
				doc.insert()
				frappe.db.commit()
				return {"success": True, "doctype": doctype, "name": doc.name, "data": doc.as_dict()}
			except Exception as e:
				frappe.db.rollback()
				return {"success": False, "error": str(e), "exc_type": type(e).__name__}

		code = f"""
    payload = {json.dumps(values)}
    doc = frappe.new_doc({json.dumps(doctype)})
    doc.update(payload)
    doc.insert()
    frappe.db.commit()
    print(json.dumps({{'success': True, 'doctype': {json.dumps(doctype)}, 'name': doc.name, 'data': doc.as_dict()}}, default=str))
"""
		return self.execute_script(code)

	def get_doc(self, doctype: str, name: str) -> dict[str, Any]:
		"""Fetch full document details."""
		if self._is_native_frappe():
			import frappe

			try:
				if not frappe.db.exists(doctype, name):
					return {"success": False, "error": f"Document {doctype} '{name}' not found"}
				doc = frappe.get_doc(doctype, name)
				return {"success": True, "doctype": doctype, "name": doc.name, "data": doc.as_dict()}
			except Exception as e:
				return {"success": False, "error": str(e), "exc_type": type(e).__name__}

		code = f"""
    if not frappe.db.exists({json.dumps(doctype)}, {json.dumps(name)}):
        print(json.dumps({{'success': False, 'error': f"Document {{{json.dumps(doctype)}}} '{{{json.dumps(name)}}}' not found"}}))
    else:
        doc = frappe.get_doc({json.dumps(doctype)}, {json.dumps(name)})
        print(json.dumps({{'success': True, 'doctype': {json.dumps(doctype)}, 'name': doc.name, 'data': doc.as_dict()}}, default=str))
"""
		return self.execute_script(code)

	def update_doc(self, doctype: str, name: str, values: dict[str, Any]) -> dict[str, Any]:
		"""Update fields on an existing document."""
		if self._is_native_frappe():
			import frappe

			try:
				doc = frappe.get_doc(doctype, name)
				doc.update(values)
				doc.save()
				frappe.db.commit()
				return {"success": True, "doctype": doctype, "name": doc.name, "data": doc.as_dict()}
			except Exception as e:
				frappe.db.rollback()
				return {"success": False, "error": str(e), "exc_type": type(e).__name__}

		code = f"""
    payload = {json.dumps(values)}
    doc = frappe.get_doc({json.dumps(doctype)}, {json.dumps(name)})
    doc.update(payload)
    doc.save()
    frappe.db.commit()
    print(json.dumps({{'success': True, 'doctype': {json.dumps(doctype)}, 'name': doc.name, 'data': doc.as_dict()}}, default=str))
"""
		return self.execute_script(code)

	def delete_doc(self, doctype: str, name: str) -> dict[str, Any]:
		"""Delete a draft or cancelled document."""
		if self._is_native_frappe():
			import frappe

			try:
				frappe.delete_doc(doctype, name)
				frappe.db.commit()
				return {"success": True, "doctype": doctype, "name": name, "message": "Deleted successfully"}
			except Exception as e:
				frappe.db.rollback()
				return {"success": False, "error": str(e), "exc_type": type(e).__name__}

		code = f"""
    frappe.delete_doc({json.dumps(doctype)}, {json.dumps(name)})
    frappe.db.commit()
    print(json.dumps({{'success': True, 'doctype': {json.dumps(doctype)}, 'name': {json.dumps(name)}, 'message': 'Deleted successfully'}}))
"""
		return self.execute_script(code)

	def submit_doc(self, doctype: str, name: str) -> dict[str, Any]:
		"""Submit a submittable document (docstatus 0 -> 1)."""
		if self._is_native_frappe():
			import frappe

			try:
				doc = frappe.get_doc(doctype, name)
				doc.submit()
				frappe.db.commit()
				return {
					"success": True,
					"doctype": doctype,
					"name": doc.name,
					"docstatus": doc.docstatus,
					"data": doc.as_dict(),
				}
			except Exception as e:
				frappe.db.rollback()
				return {"success": False, "error": str(e), "exc_type": type(e).__name__}

		code = f"""
    doc = frappe.get_doc({json.dumps(doctype)}, {json.dumps(name)})
    doc.submit()
    frappe.db.commit()
    print(json.dumps({{'success': True, 'doctype': {json.dumps(doctype)}, 'name': doc.name, 'docstatus': doc.docstatus, 'data': doc.as_dict()}}, default=str))
"""
		return self.execute_script(code)

	def cancel_doc(self, doctype: str, name: str) -> dict[str, Any]:
		"""Cancel a submitted document (docstatus 1 -> 2)."""
		if self._is_native_frappe():
			import frappe

			try:
				doc = frappe.get_doc(doctype, name)
				doc.cancel()
				frappe.db.commit()
				return {
					"success": True,
					"doctype": doctype,
					"name": doc.name,
					"docstatus": doc.docstatus,
					"message": "Cancelled successfully",
				}
			except Exception as e:
				frappe.db.rollback()
				return {"success": False, "error": str(e), "exc_type": type(e).__name__}

		code = f"""
    doc = frappe.get_doc({json.dumps(doctype)}, {json.dumps(name)})
    doc.cancel()
    frappe.db.commit()
    print(json.dumps({{'success': True, 'doctype': {json.dumps(doctype)}, 'name': doc.name, 'docstatus': doc.docstatus, 'message': 'Cancelled successfully'}}, default=str))
"""
		return self.execute_script(code)

	def search_docs(
		self,
		doctype: str,
		filters: dict[str, Any] | None = None,
		fields: list[str] | None = None,
		limit: int = 20,
	) -> dict[str, Any]:
		"""Search documents with parameterized filters."""
		if self._is_native_frappe():
			import frappe

			try:
				docs = frappe.get_all(
					doctype, filters=filters or {}, fields=fields or ["name"], limit_page_length=limit
				)
				return {"success": True, "doctype": doctype, "count": len(docs), "data": docs}
			except Exception as e:
				return {"success": False, "error": str(e), "exc_type": type(e).__name__}

		code = f"""
    flt = {json.dumps(filters or {})}
    flds = {json.dumps(fields or ['name'])}
    docs = frappe.get_all({json.dumps(doctype)}, filters=flt, fields=flds, limit_page_length={limit})
    print(json.dumps({{'success': True, 'doctype': {json.dumps(doctype)}, 'count': len(docs), 'data': docs}}, default=str))
"""
		return self.execute_script(code)

	def get_meta(self, doctype: str) -> dict[str, Any]:
		"""Retrieve live metadata and field definitions for a DocType."""
		if self._is_native_frappe():
			import frappe

			try:
				if not frappe.db.exists("DocType", doctype):
					return {"success": False, "error": f"DocType {doctype} does not exist"}
				meta = frappe.get_meta(doctype)
				fields_data = [
					{
						"fieldname": f.fieldname,
						"label": f.label,
						"fieldtype": f.fieldtype,
						"options": f.options,
						"reqd": f.reqd,
						"default": f.default,
						"read_only": f.read_only,
					}
					for f in meta.fields
					if f.fieldtype not in ("Section Break", "Column Break", "Tab Break")
				]
				return {
					"success": True,
					"doctype": doctype,
					"module": getattr(meta, "module", None),
					"is_submittable": meta.is_submittable,
					"autoname": meta.autoname,
					"fields": fields_data,
				}
			except Exception as e:
				return {"success": False, "error": str(e), "exc_type": type(e).__name__}

		code = f"""
    if not frappe.db.exists('DocType', {json.dumps(doctype)}):
        print(json.dumps({{'success': False, 'error': f"DocType {{{json.dumps(doctype)}}} does not exist"}}))
    else:
        meta = frappe.get_meta({json.dumps(doctype)})
        fields_data = [
            {{'fieldname': f.fieldname, 'label': f.label, 'fieldtype': f.fieldtype, 'options': f.options, 'reqd': f.reqd, 'default': f.default, 'read_only': f.read_only}}
            for f in meta.fields if f.fieldtype not in ('Section Break', 'Column Break', 'Tab Break')
        ]
        print(json.dumps({{'success': True, 'doctype': {json.dumps(doctype)}, 'module': getattr(meta, 'module', ''), 'is_submittable': meta.is_submittable, 'autoname': meta.autoname, 'fields': fields_data}}, default=str))
"""
		return self.execute_script(code)

	def get_link_options(self, target_doctype: str, limit: int = 100) -> list[str]:
		"""Dynamically fetch valid document names for a Link target DocType from live ERPNext database."""
		if not target_doctype:
			return []
		if self._is_native_frappe():
			import frappe

			try:
				if not frappe.db.exists("DocType", target_doctype):
					return []
				meta = frappe.get_meta(target_doctype)
				filters = {}
				if meta.has_field("enabled"):
					filters["enabled"] = 1
				elif meta.has_field("disabled"):
					filters["disabled"] = 0
				names = frappe.get_all(
					target_doctype,
					filters=filters,
					pluck="name",
					limit_page_length=limit,
					order_by="name asc",
				)
				return [str(n) for n in names]
			except Exception:
				return []

		code = f"""
    if not frappe.db.exists('DocType', {json.dumps(target_doctype)}):
        print(json.dumps({{'success': True, 'options': []}}))
    else:
        meta = frappe.get_meta({json.dumps(target_doctype)})
        filters = {{}}
        if meta.has_field('enabled'):
            filters['enabled'] = 1
        elif meta.has_field('disabled'):
            filters['disabled'] = 0
        names = frappe.get_all({json.dumps(target_doctype)}, filters=filters, pluck='name', limit_page_length={limit}, order_by='name asc')
        print(json.dumps({{'success': True, 'options': [str(n) for n in names]}}))
"""
		res = self.execute_script(code)
		if isinstance(res, dict) and res.get("success"):
			return res.get("options", [])
		return []

	def check_permission(
		self, doctype: str, perm_type: str = "read", user: str = "Administrator", doc: str | None = None
	) -> dict[str, Any]:
		"""Check user permissions on a DocType."""
		if self._is_native_frappe():
			import frappe

			try:
				has_perm = frappe.has_permission(doctype, ptype=perm_type, doc=doc, user=user)
				return {
					"success": True,
					"doctype": doctype,
					"perm_type": perm_type,
					"user": user,
					"has_permission": bool(has_perm),
				}
			except Exception as e:
				return {"success": False, "error": str(e), "exc_type": type(e).__name__}

		code = f"""
    has_perm = frappe.has_permission(
        doctype={json.dumps(doctype)},
        ptype={json.dumps(perm_type)},
        doc={doc!r},
        user={json.dumps(user)}
    )
    print(json.dumps({{'success': True, 'doctype': {json.dumps(doctype)}, 'perm_type': {json.dumps(perm_type)}, 'user': {json.dumps(user)}, 'has_permission': bool(has_perm)}}))
"""
		return self.execute_script(code)

	def get_value(self, doctype: str, filters: Any, fieldname: Any) -> dict[str, Any]:
		"""Fetch specific field values directly from Frappe database."""
		if self._is_native_frappe():
			import frappe

			try:
				val = frappe.db.get_value(doctype, filters, fieldname, as_dict=True)
				if val is None:
					return {"success": False, "error": "Record not found"}
				return {"success": True, "doctype": doctype, "data": val}
			except Exception as e:
				return {"success": False, "error": str(e), "exc_type": type(e).__name__}

		code = f"""
    val = frappe.db.get_value({json.dumps(doctype)}, {json.dumps(filters)}, {json.dumps(fieldname)}, as_dict=True)
    if val is None:
        print(json.dumps({{'success': False, 'error': 'Record not found'}}))
    else:
        print(json.dumps({{'success': True, 'doctype': {json.dumps(doctype)}, 'data': val}}, default=str))
"""
		return self.execute_script(code)

	def get_count(self, doctype: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
		"""Count records matching filters."""
		if self._is_native_frappe():
			import frappe

			try:
				count = frappe.db.count(doctype, filters=filters or {})
				return {"success": True, "doctype": doctype, "count": count}
			except Exception as e:
				return {"success": False, "error": str(e), "exc_type": type(e).__name__}

		code = f"""
    count = frappe.db.count({json.dumps(doctype)}, filters={json.dumps(filters or {})})
    print(json.dumps({{'success': True, 'doctype': {json.dumps(doctype)}, 'count': count}}))
"""
		return self.execute_script(code)

	def exists(self, doctype: str, filters: Any) -> bool:
		"""Check if a record exists in Frappe."""
		if self._is_native_frappe():
			import frappe

			try:
				return bool(frappe.db.exists(doctype, filters))
			except Exception:
				return False

		code = f"""
    res = bool(frappe.db.exists({json.dumps(doctype)}, {json.dumps(filters)}))
    print(json.dumps({{'success': True, 'exists': res}}))
"""
		res = self.execute_script(code)
		return bool(res.get("exists", False))
