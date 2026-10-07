"""Read-back Validation Engine for ERPNext AI Agent.

Guarantees data integrity by querying Frappe/ERPNext immediately after any mutation
to verify that records were actually created, modified, submitted, or cancelled with
the expected attributes.
"""

from typing import Any, Dict, Optional

from ERPNext_Agent.tools.client import FrappeClient


class ReadBackValidator:
	"""Performs strict read-back verification on mutation results."""

	def __init__(self, client: FrappeClient):
		self.client = client

	def verify_document_created(
		self, doctype: str, name: str, expected_fields: dict[str, Any] | None = None
	) -> dict[str, Any]:
		"""Verify that a document was created and fields match expectations."""
		res = self.client.get_doc(doctype, name)
		if not res.get("success"):
			return {
				"verified": False,
				"reason": f"Document {doctype} '{name}' could not be fetched after creation: {res.get('error')}",
				"doc": None,
			}
		doc = res.get("data", {})
		mismatches = []
		if expected_fields:
			for k, expected_v in expected_fields.items():
				if k in doc and expected_v is not None:
					# Compare string representations to handle Decimals, Dates, and Ints cleanly
					if str(doc.get(k)) != str(expected_v):
						mismatches.append(
							f"Field '{k}' mismatch: expected '{expected_v}', got '{doc.get(k)}'"
						)

		if mismatches:
			return {"verified": False, "reason": "; ".join(mismatches), "doc": doc}

		return {
			"verified": True,
			"doctype": doctype,
			"name": name,
			"docstatus": doc.get("docstatus", 0),
			"doc": doc,
		}

	def verify_document_updated(
		self, doctype: str, name: str, updated_fields: dict[str, Any]
	) -> dict[str, Any]:
		"""Verify that modified fields have taken effect."""
		return self.verify_document_created(doctype, name, expected_fields=updated_fields)

	def verify_document_status(self, doctype: str, name: str, expected_docstatus: int) -> dict[str, Any]:
		"""Verify document docstatus (0=Draft, 1=Submitted, 2=Cancelled)."""
		res = self.client.get_doc(doctype, name)
		if not res.get("success"):
			return {
				"verified": False,
				"reason": f"Failed to retrieve {doctype} '{name}': {res.get('error')}",
				"doc": None,
			}

		doc = res.get("data", {})
		current_status = doc.get("docstatus", 0)
		status_map = {0: "Draft", 1: "Submitted", 2: "Cancelled"}

		if current_status != expected_docstatus:
			return {
				"verified": False,
				"reason": (
					f"Docstatus mismatch for {doctype} '{name}': "
					f"expected {expected_docstatus} ({status_map.get(expected_docstatus)}), "
					f"found {current_status} ({status_map.get(current_status)})"
				),
				"doc": doc,
			}

		return {
			"verified": True,
			"doctype": doctype,
			"name": name,
			"docstatus": current_status,
			"status_label": status_map.get(current_status, "Unknown"),
			"doc": doc,
		}

	def verify_stock_availability(
		self, item_code: str, warehouse: str, required_qty: float
	) -> dict[str, Any]:
		"""Pre-transaction check: ensure warehouse has sufficient actual_qty."""
		res = self.client.search_docs(
			doctype="Bin",
			filters={"item_code": item_code, "warehouse": warehouse},
			fields=["actual_qty", "reserved_qty", "projected_qty"],
			limit=1,
		)
		if not res.get("success") or not res.get("data"):
			return {
				"verified": False,
				"available": False,
				"actual_qty": 0.0,
				"required_qty": required_qty,
				"reason": f"No Bin record found for Item '{item_code}' in Warehouse '{warehouse}'.",
			}

		bin_data = res["data"][0]
		actual_qty = float(bin_data.get("actual_qty") or 0.0)
		if actual_qty < required_qty:
			return {
				"verified": False,
				"available": False,
				"actual_qty": actual_qty,
				"required_qty": required_qty,
				"reason": f"Insufficient stock: actual {actual_qty} < required {required_qty} in '{warehouse}'.",
			}

		return {
			"verified": True,
			"available": True,
			"actual_qty": actual_qty,
			"required_qty": required_qty,
			"projected_qty": float(bin_data.get("projected_qty") or 0.0),
		}
