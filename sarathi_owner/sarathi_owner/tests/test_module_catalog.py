"""Integration contract for live module discovery. All fixtures are rolled back."""
import unittest
from unittest.mock import patch

import frappe

from sarathi_owner.api import module_catalog as catalog


class TestModuleCatalog(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.init("frontend")
		frappe.connect()
		frappe.set_user("Administrator")

	def setUp(self):
		frappe.set_user("Administrator")
		frappe.db.savepoint("catalog_test")

	def tearDown(self):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="catalog_test")
		frappe.clear_cache(doctype="Customer")

	def test_guest_denied(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			catalog.get_catalog()

	def test_native_invoicing_coverage(self):
		data = catalog.get_catalog()
		module = next(m for m in data["modules"] if m["id"] == "invoicing")
		source = frappe.get_doc("Workspace Sidebar", "Invoicing")
		targets = {(e["kind"], e["target"]) for e in module["entries"]}
		for row in source.items:
			if row.type == "Link":
				self.assertIn((row.link_type, row.link_to), targets)
		self.assertTrue(catalog.get_catalog(data["revision"])["unchanged"])

	def test_external_and_recursive_routes_not_embedded(self):
		self.assertIsNone(catalog._route({"link_type": "URL", "url": "https://example.com"}))
		self.assertIsNone(catalog._route({"link_type": "URL", "url": "//example.com/app/customer"}))
		self.assertIsNone(catalog._route({"link_type": "Page", "link_to": "sarathiownertower"}))

	def test_entry_cannot_be_forged(self):
		with self.assertRaises(frappe.PermissionError):
			catalog.get_entry("invoicing", "forged-entry-id")

	def test_new_sidebar_entry_appears_without_code_changes(self):
		before = catalog.get_catalog()["revision"]
		doc = frappe.get_doc("Workspace Sidebar", "Invoicing")
		doc.append(
			"items",
			{
				"type": "Link",
				"label": "Catalog test directory",
				"link_type": "DocType",
				"link_to": "Customer",
			},
		)
		with patch.dict(frappe.conf, {"developer_mode": 0}):
			doc.save()
		data = catalog.get_catalog(before)
		self.assertNotEqual(data["revision"], before)
		module = next(m for m in data["modules"] if m["id"] == "invoicing")
		self.assertTrue(any(e["label"] == "Catalog test directory" for e in module["entries"]))

	def test_new_field_detected_without_frontend_change(self):
		before = catalog.get_catalog()["revision"]
		# This tests metadata discovery, not MariaDB DDL (which implicitly commits).
		with patch.object(frappe.db, "updatedb"):
			frappe.get_doc(
				{
					"doctype": "Custom Field",
					"dt": "Customer",
					"fieldname": "custom_catalog_test",
					"label": "Catalog test field",
					"fieldtype": "Data",
					"insert_after": "customer_name",
				}
			).insert()
		frappe.clear_cache(doctype="Customer")
		data = catalog.get_catalog(before)
		self.assertNotEqual(data["revision"], before)
		module = next(m for m in data["modules"] if m["id"] == "invoicing")
		entry = next(e for e in module["entries"] if e["target"] == "Customer")
		detail = catalog.get_entry(module["id"], entry["id"])
		self.assertTrue(any(f["fieldname"] == "custom_catalog_test" for f in detail["schema"]))

	def test_records_and_children_are_permission_checked(self):
		data = catalog.get_catalog()
		module = next(m for m in data["modules"] if m["id"] == "invoicing")
		entry = next(e for e in module["entries"] if e["target"] == "Sales Invoice" and not e["filters"])
		listing = catalog.get_entry(module["id"], entry["id"])
		self.assertLessEqual(len(listing["rows"]), 25)
		if listing["rows"]:
			record = catalog.get_entry(module["id"], entry["id"], name=listing["rows"][0]["name"])
			self.assertTrue(any(t["label"] == "Items" for t in record["tables"]))
		with patch("frappe.has_permission", return_value=False):
			with self.assertRaises(frappe.PermissionError):
				catalog.get_entry(module["id"], entry["id"])

	def test_restricted_user_catalog(self):
		user = frappe.get_doc(
			{
				"doctype": "User",
				"email": "catalog-test@example.invalid",
				"first_name": "Catalog Test",
				"user_type": "System User",
				"send_welcome_email": 0,
				"roles": [{"role": "Stock User"}],
			}
		).insert()
		frappe.set_user(user.name)
		data = catalog.get_catalog()
		targets = {e["target"] for m in data["modules"] for e in m["entries"] if e["kind"] == "DocType"}
		self.assertIn("Item", targets)
		self.assertNotIn("System Settings", targets)
		for module in data["modules"]:
			for entry in module["entries"]:
				if entry["kind"] == "DocType":
					self.assertTrue(frappe.has_permission(entry["target"], "read"))
		with self.assertRaises(frappe.PermissionError):
			catalog.get_entry("invoicing", "not-visible")

	def test_events_are_payload_free_and_post_commit(self):
		with patch("frappe.publish_realtime") as publish:
			catalog.broadcast_change(frappe._dict(doctype="Sales Invoice"))
			publish.assert_called_with("sarathi_records_changed", {}, after_commit=True)
			catalog.broadcast_change(frappe._dict(doctype="Custom Field"))
			publish.assert_called_with("sarathi_catalog_changed", {}, after_commit=True)
