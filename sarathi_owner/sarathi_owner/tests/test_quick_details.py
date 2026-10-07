"""Coverage for embedded action routing, filtering, and permissions."""
import unittest
from unittest.mock import patch

import frappe

from sarathi_owner.api.quick_details import get_details


class TestQuickDetails(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.init("frontend")
		frappe.connect()

	def setUp(self):
		frappe.set_user("Administrator")

	def tearDown(self):
		frappe.set_user("Administrator")

	def test_external_routes_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			get_details("https://example.com/app/customer")

	def test_unlisted_doctype_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			get_details("/app/user")

	def test_guest_cannot_read(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			get_details("/app/customer")

	def test_document_read_permission_enforced(self):
		with patch("sarathi_owner.api.quick_details.frappe.has_permission", return_value=False):
			with self.assertRaises(frappe.PermissionError):
				get_details("/app/sales-invoice")

	def test_new_action_is_read_only_list(self):
		data = get_details("/app/sales-invoice/new-sales-invoice-1")
		self.assertEqual(data["kind"], "list")
		self.assertLessEqual(len(data["result"]), 25)

	def test_credit_notes_preserve_route_filter(self):
		data = get_details("/app/sales-invoice?is_return=1")
		for row in data["result"]:
			self.assertEqual(frappe.db.get_value("Sales Invoice", row["name"], "is_return"), 1)

	def test_record_detail_is_safe(self):
		data = get_details("/app/customer")
		if not data["result"]:
			self.skipTest("No visible customer records")
		record = get_details("/app/customer", name=data["result"][0]["name"])
		self.assertEqual(record["kind"], "record")
		self.assertTrue(all(f["fieldtype"] not in ("Password", "HTML", "Table") for f in record["fields"]))

	def test_nested_workspace_and_tool_keep_their_identity(self):
		from sarathi_owner.api.module_catalog import _modules

		entries = next(m for m in _modules() if m["id"] == "invoicing")["entries"]
		home = next(e for e in entries if e["label"] == "Home")
		data = get_details(home["route"], entry_id=home["id"])
		self.assertEqual(data["kind"], "workspace")
		self.assertTrue(any(e["target"] == "Sales Invoice" for e in data["entries"]))
		tool = next(e for e in entries if e["target"] == "Payment Reconciliation")
		result = get_details(tool["route"], entry_id=tool["id"])
		self.assertEqual(result["kind"], "list")
		self.assertEqual(result["doctype"], "Payment Entry")

	def test_financial_report_stays_inside_dashboard(self):
		data = get_details("/desk/query-report/General%20Ledger")
		self.assertEqual(data["kind"], "list")
		self.assertEqual(data["doctype"], "Journal Entry")

	def test_every_finance_entry_has_an_in_dashboard_response(self):
		from sarathi_owner.api.module_catalog import _modules

		labels = {
			"Invoicing",
			"Payments",
			"Financial Reports",
			"Accounts Setup",
			"Taxes",
			"Banking",
			"Budget",
			"Share Management",
			"Subscription",
		}
		entries = [entry for module in _modules() if module["label"] in labels for entry in module["entries"]]
		self.assertTrue(entries)
		for entry in entries:
			with self.subTest(entry=entry["label"]):
				data = get_details(entry.get("route"), entry_id=entry["id"])
				self.assertIn(data["kind"], {"list", "record", "workspace"})
				if entry["kind"] in {"Report", "Page"}:
					self.assertEqual(data["kind"], "list")

	def test_search_scopes_calculations_and_chart(self):
		data = get_details("/app/sales-invoice", search="NONEXISTENT-AUDIT-RECORD-9c814")
		self.assertEqual(data["total_count"], 0)
		self.assertEqual(data["calculations"][0]["value"], 0)
		self.assertEqual(data["charts"], [])

	def test_forged_nested_entry_is_rejected(self):
		with self.assertRaises(frappe.PermissionError):
			get_details("/app/customer", entry_id="forged")

	def test_invoice_child_tables_are_visible(self):
		data = get_details("/app/sales-invoice")
		if not data["result"]:
			self.skipTest("An invoice is needed")
		record = get_details("/app/sales-invoice", name=data["result"][0]["name"])
		self.assertTrue(any(t["label"] == "Items" for t in record["tables"]))

	def test_invoice_calculations_keep_return_filter(self):
		data = get_details("/app/sales-invoice?is_return=1")
		names = frappe.get_list("Sales Invoice", filters={"is_return": 1}, pluck="name", limit_page_length=0)
		self.assertEqual(data["total_count"], len(names))
		self.assertEqual(sum(data["charts"][0]["datasets"][0]["values"]) if data["charts"] else 0, len(names))
