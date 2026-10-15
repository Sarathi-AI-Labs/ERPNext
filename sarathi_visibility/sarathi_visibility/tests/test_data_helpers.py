"""Native-permission integration tests, with DASH-003 transactional fixtures."""
import unittest
from unittest.mock import patch

import frappe

from sarathi_visibility.api import data_helpers as helpers
from sarathi_visibility.tests.test_permissions import PermissionTests


class DataHelperTests(PermissionTests):
	# Inherit the existing nineteen security regressions and their rollback fixtures.
	def test_strict_pagination(self):
		self.assertEqual(helpers.pagination("10", "25"), (10, 25))
		for start, length in [(-1, 25), (0, 0), (0, 101), (0, "1; DROP TABLE"), (False, 25), (1.5, 25), (100001, 25)]:
			with self.subTest(start=start, length=length), self.assertRaises(frappe.ValidationError):
				helpers.pagination(start, length)

	def test_filter_allowlists_types_and_dates(self):
		base = {"company": self.companies[0]}
		for extra in [{"shift": "day"}, {"warehouse": "x"}, {"from_date": "2026-2-01"}, {"from_date": "2026-02-30"}, {"from_date": "2026-03-01", "to_date": "2026-02-01"}, {"status": "invented"}, {"customer": ["in", self.customers]}, {"docstatus": True}]:
			with self.subTest(extra=extra), self.assertRaises(frappe.ValidationError):
				helpers.get_records("projects", {**base, **extra})
		for value in [[], '[]', '{', 5]:
			with self.assertRaises(frappe.ValidationError):
				helpers.get_records("projects", value)

	def test_sorting_resource_and_query_parameter_allowlists(self):
		for args in [{"sort_by": "name desc; SELECT 1"}, {"sort_by": "grand_total"}, {"sort_direction": "DESC"}, {"fields": ["*"]}, {"ignore_permissions": True}, {"doctype": "User"}]:
			with self.subTest(args=args), self.assertRaises(frappe.ValidationError):
				helpers.get_records("projects", {"company": self.companies[0]}, **args)
		with self.assertRaises(frappe.ValidationError):
			helpers.get_records("User")

	def test_ambiguous_company_never_picks_first(self):
		with self.assertRaises(frappe.ValidationError):
			helpers.get_records("projects")
		self.user("manager")
		rows = helpers.get_records("projects")
		self.assertEqual(rows["applied_filters"]["company"], self.companies[0])

	def test_company_and_record_filter_tampering(self):
		self.user("manager")
		allowed = helpers.get_record("projects", self.projects[0], {"company": self.companies[0]})
		self.assertEqual(allowed["name"], self.projects[0])
		for resource, name in [("projects", self.projects[1]), ("customers", self.customers[1]), ("warehouses", self.warehouses[1])]:
			with self.subTest(resource=resource), self.assertRaises(frappe.PermissionError):
				helpers.get_record(resource, name, {"company": self.companies[0]} if resource != "customers" else None)
		with self.assertRaises(frappe.PermissionError):
			helpers.get_records("projects", {"company": self.companies[1]})
		with self.assertRaises(frappe.PermissionError):
			helpers.get_records("projects", {"company": self.companies[0], "customer": self.customers[1]})

	def test_absent_company_and_missing_id_are_denied(self):
		for filters in [{"company": "DASH006-NOT-A-COMPANY"}, {"company": self.companies[0], "name": "DASH006-MISSING"}]:
			with self.assertRaises(frappe.PermissionError):
				helpers.get_records("projects", filters)

	def test_options_and_counts_do_not_leak_other_customer(self):
		self.user("manager")
		result = helpers.get_options("customers", search=self.token)
		self.assertEqual([r["value"] for r in result["options"]], [self.customers[0]])
		self.assertEqual(helpers.get_count("customers")["count"], 1)
		self.assertEqual(helpers.get_count("projects", {"company": self.companies[0], "customer": self.customers[0]})["count"], 1)
		self.assertEqual(helpers.get_options("customers", search="NOT-A-RECORD")["options"], [])

	def test_shared_masters_reject_fake_company_filter(self):
		for resource in ("customers", "workstations"):
			with self.assertRaises(frappe.ValidationError):
				helpers.get_options(resource, {"company": self.companies[0]})

	def test_no_broad_endpoint_for_shop_or_unrelated_roles(self):
		for user in ("operator", "supervisor", "unrelated", "finance_only"):
			self.user(user)
			for fn in (helpers.get_records, helpers.get_options, helpers.get_count):
				with self.assertRaises(frappe.PermissionError):
					fn("job_cards", {"company": self.companies[0]})
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			helpers.get_records("customers")

	def test_shop_read_is_explicitly_assignment_scoped(self):
		self.user("operator")
		self.assertEqual(helpers.get_shop_job(self.jobs[0].name)["name"], self.jobs[0].name)
		with self.assertRaises(frappe.PermissionError):
			helpers.get_shop_job(self.jobs[1].name)

	def test_whitelist_is_read_only(self):
		for fn in (helpers.get_records, helpers.get_record, helpers.get_options, helpers.get_count):
			self.assertEqual(frappe.allowed_http_methods_for_whitelisted_func[fn], ["GET"])
		with self.assertRaises(frappe.ValidationError):
			helpers.get_records("projects", {"company": self.companies[0]}, changes={"status": "Completed"})

	def test_stable_pages_empty_pages_and_safe_fields(self):
		first = helpers.get_records("projects", {"company": self.companies[0]}, page_length=1, sort_by="status")
		second = helpers.get_records("projects", {"company": self.companies[0]}, start=1, page_length=1, sort_by="status")
		self.assertTrue(first["has_next"])
		self.assertNotEqual(first["rows"][0]["name"], second["rows"][0]["name"])
		self.assertEqual(helpers.get_records("projects", {"company": self.companies[0]}, start=100000)["rows"], [])
		self.assertLessEqual(set(first["rows"][0]), set(helpers.RESOURCES["projects"].fields))
		self.assertNotIn("total_costing_amount", first["rows"][0])

	def test_field_permissions_are_applied_to_selection_and_sort(self):
		original = helpers.allowed_fields
		with patch.object(helpers, "allowed_fields", side_effect=lambda dt: original(dt) - {"project_name"}):
			result = helpers.get_records("projects", {"company": self.companies[0]})
			self.assertTrue(all("project_name" not in row for row in result["rows"]))
			with self.assertRaises(frappe.ValidationError):
				helpers.get_records("projects", {"company": self.companies[0]}, sort_by="project_name")

	def test_pagination_is_bounded_without_per_row_document_loads(self):
		with patch.object(helpers, "check_record", wraps=helpers.check_record) as check:
			result = helpers.get_records("projects", {"company": self.companies[0]}, page_length=100)
			self.assertLessEqual(len(result["rows"]), 100)
			self.assertLessEqual(check.call_count, 2)  # Company validation, not each result.

	def test_legacy_report_rejects_pagination_before_loading(self):
		from sarathi_visibility.api.dashboard import get_report
		with patch("sarathi_visibility.api.dashboard.load") as load:
			with self.assertRaises(frappe.ValidationError):
				get_report(start=-1)
			load.assert_not_called()

	def test_work_order_and_job_card_ids_obey_native_user_permissions(self):
		# Independent native user: avoid Customer fixture restrictions masking the target rule.
		user = f"dash006-{self.token}-ids@example.invalid"
		frappe.get_doc(dict(doctype="User", email=user, first_name="Scoped read test", send_welcome_email=0,
			roles=[dict(role=r) for r in ("Manufacturing Manager", "Manufacturing User", "Stock User", "Projects User")])).insert()
		try:
			for resource, dt in (("work_orders", "Work Order"), ("job_cards", "Job Card")):
				frappe.set_user("Administrator")
				rows = frappe.get_all(dt, fields=["name", "company"], limit=2, order_by="name asc")
				self.assertEqual(len(rows), 2, "Two native manufacturing records required")
				permission = frappe.get_doc(dict(doctype="User Permission", user=user, allow=dt,
					for_value=rows[0].name, apply_to_all_doctypes=1)).insert()
				frappe.clear_cache(user=user)
				frappe.set_user(user)
				self.assertEqual(helpers.get_record(resource, rows[0].name, {"company": rows[0].company})["name"], rows[0].name)
				with self.assertRaises(frappe.PermissionError):
					helpers.get_record(resource, rows[1].name, {"company": rows[1].company})
				self.assertEqual(helpers.get_count(resource, {"company": rows[0].company})["count"], 1)
				frappe.set_user("Administrator")
				permission.delete()
				frappe.clear_cache(user=user)
		finally:
			frappe.set_user("Administrator")
			# Rollback fixture lifecycle in parent teardown handles the inserted user.
			frappe.clear_cache(user=user)

	def test_internal_errors_are_not_empty_results_or_secret_messages(self):
		with patch.object(helpers, "_resource", side_effect=RuntimeError("SECRET SQL TRACE")), patch.object(frappe, "log_error") as log:
			with self.assertRaises(helpers.DashboardReadError) as raised:
				helpers.get_records("projects")
			self.assertNotIn("SECRET", str(raised.exception))
			self.assertEqual(log.call_count, 1)
			self.assertTrue(frappe.local.flags.disable_traceback)

	def test_datetime_end_date_is_exclusive_next_day(self):
		conditions, applied = helpers.validated_filters(helpers.RESOURCES["work_orders"],
			{"company": self.companies[0], "from_date": "2026-01-01", "to_date": "2026-01-31"})
		self.assertIn(["planned_start_date", ">=", "2026-01-01"], conditions)
		self.assertIn(["planned_start_date", "<", "2026-02-01"], conditions)

	def test_read_endpoints_do_not_save_documents(self):
		from frappe.model.document import Document
		self.user("manager")
		with patch.object(Document, "save", side_effect=AssertionError("Read attempted a write")):
			helpers.get_records("projects", {"company": self.companies[0]})
			helpers.get_options("customers")
			helpers.get_count("customers")

	def test_wildcard_option_search_is_literal(self):
		self.user("manager")
		self.assertEqual(helpers.get_options("customers", search="%_")["options"], [])


def run():
	suite = unittest.defaultTestLoader.loadTestsFromTestCase(DataHelperTests)
	result = unittest.TextTestRunner(verbosity=2).run(suite)
	frappe.db.rollback()
	if not result.wasSuccessful():
		raise AssertionError("DASH-006 helper tests failed")
	return {"tests": result.testsRun, "skipped": len(result.skipped), "passed": True}
