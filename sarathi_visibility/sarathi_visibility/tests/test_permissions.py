"""DASH-003 integration tests against native permissions; fixtures roll back."""

import unittest
from unittest.mock import patch

import frappe
from sarathi_visibility.api.access import (
	DENIED,
	check_shop_job,
	operational_payload,
	save_draft_changes,
	scoped_rows,
	scoped_sql,
	validate_filters,
)
from sarathi_visibility.api.dashboard import get_summary, associate_customer
from sarathi_visibility.api.accounting import get_accounting_dashboard
from sarathi_visibility.api.control_tower import update_project, sync_tubepro
from sarathi_owner.api.owner_dashboard import get_owner_summary, clear_owner_cache, get_live_report_data
from sarathi_visibility.setup.install import ensure_dashboard_roles


class PermissionTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.set_user("Administrator")
		frappe.db.savepoint("dash003_permissions")
		ensure_dashboard_roles()
		cls.token = frappe.generate_hash(length=8)
		cls.companies = frappe.get_all("Company", pluck="name", limit=2)
		assert len(cls.companies) == 2, "Two native companies required for security tests"
		cls.jobs = frappe.get_all("Job Card", fields=["name", "workstation", "company"], limit=3)
		assert len(cls.jobs) >= 2, "Two native Job Cards required for assignment tests"
		cls.users = {}
		combinations = {
			"owner": [
				"Sarathi Owner",
				"Accounts User",
				"Projects User",
				"Manufacturing User",
				"Sales User",
				"Stock User",
			],
			"manager": ["Manufacturing Manager", "Projects User", "Sales User", "Stock User"],
			"supervisor": ["Sarathi Supervisor", "Manufacturing User", "Stock User"],
			"operator": ["Sarathi Operator", "Manufacturing User", "Stock User"],
			"unrelated": ["Manufacturing User"],
			"finance_only": ["Accounts User"],
			"setup": ["Sarathi Super Admin"],
		}
		for label, roles in combinations.items():
			user = f"dash003-{cls.token}-{label}@example.invalid"
			frappe.get_doc(
				dict(
					doctype="User",
					email=user,
					first_name=label,
					send_welcome_email=0,
					roles=[dict(role=r) for r in roles],
				)
			).insert()
			cls.users[label] = user
		cls.customers = []
		cls.warehouses = []
		group = frappe.get_all("Customer Group", filters={"is_group": 0}, pluck="name", limit=1)[0]
		territory = frappe.get_all("Territory", filters={"is_group": 0}, pluck="name", limit=1)[0]
		for idx, company in enumerate(cls.companies):
			customer = frappe.get_doc(
				dict(
					doctype="Customer",
					customer_name=f"DASH003 {cls.token} {idx}",
					customer_type="Company",
					customer_group=group,
					territory=territory,
				)
			).insert()
			cls.customers.append(customer.name)
			warehouse = frappe.get_doc(
				dict(doctype="Warehouse", warehouse_name=f"DASH003 {cls.token} {idx}", company=company)
			).insert()
			cls.warehouses.append(warehouse.name)
		cls.projects = []
		for idx, company in enumerate(cls.companies):
			doc = frappe.get_doc(
				dict(
					doctype="Project",
					project_name=f"DASH003 {cls.token} {idx}",
					company=company,
					customer=cls.customers[idx],
				)
			).insert()
			cls.projects.append(doc.name)
		for label in ("owner", "manager"):
			frappe.get_doc(
				dict(
					doctype="User Permission",
					user=cls.users[label],
					allow="Company",
					for_value=cls.companies[0],
					apply_to_all_doctypes=1,
				)
			).insert()
			frappe.get_doc(
				dict(
					doctype="User Permission",
					user=cls.users[label],
					allow="Customer",
					for_value=cls.customers[0],
					apply_to_all_doctypes=1,
				)
			).insert()
		cls.todos = []
		for label in ("operator", "supervisor"):
			todo = frappe.get_doc(
				dict(
					doctype="ToDo",
					description="DASH003 isolated assignment",
					allocated_to=cls.users[label],
					reference_type="Job Card",
					reference_name=cls.jobs[0].name,
				)
			).insert()
			cls.todos.append(todo.name)

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="dash003_permissions")
		for user in cls.users.values():
			frappe.clear_cache(user=user)

	def tearDown(self):
		frappe.set_user("Administrator")

	def user(self, label):
		frappe.set_user(self.users[label])

	def test_owner_allowed_but_manager_not_executive(self):
		self.user("owner")
		self.assertIn("cards", get_owner_summary({"company": self.companies[0]}))
		self.user("manager")
		with self.assertRaises(frappe.PermissionError):
			get_owner_summary()
		with self.assertRaises(frappe.PermissionError):
			clear_owner_cache()

	def test_manager_operational_summary_hides_financials(self):
		self.user("manager")
		result = get_summary({"company": self.companies[0]})
		self.assertIn("production_summary", result)
		self.assertTrue(result["accounting_summary"]["restricted"])
		self.assertNotIn("financial_trend", result)
		with self.assertRaises(frappe.PermissionError):
			get_accounting_dashboard()
		self.assertEqual(scoped_rows("GL Entry", fields=["name", "debit"]), [])
		raw = operational_payload({"count": 3, "value": 4, "total": 5, "stock_value": 100, "cost": 80})
		self.assertEqual(raw, {"count": 3, "value": 4, "total": 5})

	def test_no_direct_endpoints_without_capability(self):
		for label in ("operator", "supervisor", "unrelated", "finance_only"):
			self.user(label)
			for fn in (get_summary, get_owner_summary, get_accounting_dashboard):
				with self.assertRaises(frappe.PermissionError):
					fn()

	def test_native_report_rejects_unverified_record_scopes(self):
		self.user("owner")
		with self.assertRaises(frappe.PermissionError):
			get_live_report_data("General Ledger", {"company": self.companies[0]})

	def test_installed_page_permissions_and_post_only_mutations(self):
		for label, owner, production in (
			("owner", True, True),
			("manager", False, True),
			("supervisor", False, False),
			("operator", False, False),
			("unrelated", False, False),
		):
			self.user(label)
			self.assertEqual(bool(frappe.get_doc("Page", "sarathiownertower").is_permitted()), owner)
			self.assertEqual(bool(frappe.get_doc("Page", "sarathicontroltower").is_permitted()), production)
		for fn in (update_project, sync_tubepro, clear_owner_cache):
			self.assertEqual(frappe.allowed_http_methods_for_whitelisted_func[fn], ["POST"])

	def test_filtered_finance_queries_do_not_swallow_sql_errors(self):
		from sarathi_visibility.api import accounting

		self.user("owner")
		errors = []
		query = accounting.scoped_sql

		def checked(*args, **kwargs):
			try:
				return query(*args, **kwargs)
			except Exception as exc:
				errors.append(type(exc).__name__)
				raise

		with patch.object(accounting, "scoped_sql", side_effect=checked) as calls:
			result = get_accounting_dashboard({"company": self.companies[0]})
		self.assertTrue(result)
		self.assertGreater(calls.call_count, 6)
		self.assertEqual(errors, [])

	def test_guest_denied(self):
		frappe.set_user("Guest")
		with self.assertRaises(frappe.PermissionError):
			get_summary()

	def test_company_and_record_filters_fail_closed(self):
		for label in ("owner", "manager"):
			self.user(label)
			self.assertEqual(validate_filters({"company": self.companies[0]})["company"], self.companies[0])
			for filters in (
				{"company": self.companies[1]},
				{"project": self.projects[1]},
				{"project": "DASH003-does-not-exist"},
				{"warehouse": ["in", ["anything"]]},
				{"warehouse": self.warehouses[1]},
				{"customer": self.customers[1]},
			):
				with self.assertRaises(frappe.PermissionError):
					get_summary(filters)
			with self.assertRaises(frappe.ValidationError):
				validate_filters("[]")
			with self.assertRaises(frappe.ValidationError):
				validate_filters({"from_date": "2026-12-01", "to_date": "2026-01-01"})

	def test_sql_scope_matches_native_rows_and_nested_join(self):
		self.user("manager")
		native = {r.name for r in frappe.get_list("Project", fields=["name"], limit_page_length=0)}
		rows = scoped_sql(
			"SELECT p.name FROM `tabProject` p JOIN `tabCompany` c ON c.name=p.company", as_dict=True
		)
		self.assertEqual({r.name for r in rows}, native)
		self.assertIn(self.projects[0], native)
		self.assertNotIn(self.projects[1], native)
		self.assertEqual(scoped_sql("SELECT COUNT(*) FROM `tabProject`")[0][0], len(native))
		rows = scoped_sql(
			"SELECT name FROM `tabProject` WHERE company IN (SELECT name FROM `tabCompany`)", as_dict=True
		)
		self.assertEqual({r.name for r in rows}, native)
		with self.assertRaises(frappe.PermissionError):
			scoped_sql("DELETE FROM `tabProject`")
		with self.assertRaises(frappe.PermissionError):
			scoped_sql("SELECT * FROM `tabProject`; SELECT 1")

	def test_sql_child_rows_and_currency_masking(self):
		self.user("manager")
		permitted = {r.name for r in frappe.get_list("Work Order", fields=["name"], limit_page_length=0)}
		children = scoped_rows("Work Order Item", fields=["name", "parent"])
		self.assertTrue(all(r.parent in permitted for r in children))
		expected = frappe.get_all(
			"Work Order Item", filters={"parent": ["in", list(permitted)]}, pluck="name"
		)
		self.assertEqual({r.name for r in children}, set(expected))
		orders = scoped_rows("Sales Order", fields=["name", "grand_total"])
		self.assertTrue(all(r.grand_total is None for r in orders))
		rows = scoped_sql("SELECT grand_total FROM `tabSales Order`", as_dict=True)
		self.assertTrue(all(r.grand_total is None for r in rows))

	def test_operator_assignment_positive_and_forged_id_negative(self):
		self.user("operator")
		self.assertEqual(check_shop_job(self.jobs[0].name).name, self.jobs[0].name)
		for name in (self.jobs[1].name, "DASH003-not-a-job"):
			with self.assertRaises(frappe.PermissionError) as exc:
				check_shop_job(name)
			self.assertIn(DENIED, str(exc.exception))
		with self.assertRaises(frappe.PermissionError):
			check_shop_job(self.jobs[0].name, "submit")

	def test_supervisor_team_is_not_factory_access(self):
		self.user("supervisor")
		self.assertEqual(check_shop_job(self.jobs[0].name).name, self.jobs[0].name)
		with self.assertRaises(frappe.PermissionError):
			check_shop_job(self.jobs[1].name)
		frappe.set_user("Administrator")
		workstation = self.jobs[1].workstation
		frappe.get_doc(
			dict(
				doctype="User Permission",
				user=self.users["supervisor"],
				allow="Workstation",
				for_value=workstation,
				apply_to_all_doctypes=0,
				applicable_for="Job Card",
			)
		).insert()
		self.user("supervisor")
		self.assertEqual(check_shop_job(self.jobs[1].name).name, self.jobs[1].name)

	def test_empty_assignment_denies_job(self):
		frappe.db.set_value("ToDo", self.todos[0], "status", "Closed")
		try:
			self.user("operator")
			with self.assertRaises(frappe.PermissionError):
				check_shop_job(self.jobs[0].name)
		finally:
			frappe.set_user("Administrator")
			frappe.db.set_value("ToDo", self.todos[0], "status", "Open")

	def test_legacy_action_requires_capability_and_native_write(self):
		before = frappe.db.get_value("Project", self.projects[0], "project_name")
		for label in ("manager", "operator", "setup"):
			self.user(label)
			with self.assertRaises(frappe.PermissionError):
				update_project(self.projects[0], {"project_name": "forged"})
		frappe.set_user("Administrator")
		self.assertEqual(frappe.db.get_value("Project", self.projects[0], "project_name"), before)

	def test_native_draft_edit_and_invalid_transition(self):
		result = update_project(self.projects[0], {"project_name": f"DASH003 edited {self.token}"})
		self.assertTrue(result["success"])
		with self.assertRaises(frappe.ValidationError):
			update_project(self.projects[0], {"status": "Completed"})
		with patch("frappe.model.workflow.get_workflow_name", return_value="Test active workflow"):
			with self.assertRaises(frappe.ValidationError):
				save_draft_changes("Project", self.projects[0], {"project_name": "bad"}, {"project_name"})
		frappe.db.set_value("Project", self.projects[0], "docstatus", 1)
		try:
			with self.assertRaises(frappe.ValidationError):
				save_draft_changes("Project", self.projects[0], {"project_name": "bad"}, {"project_name"})
		finally:
			frappe.db.set_value("Project", self.projects[0], "docstatus", 0)

	def test_customer_link_retry_is_idempotent(self):
		first = associate_customer(self.companies[0], self.customers[0])
		self.assertEqual(associate_customer(self.companies[0], self.customers[0]), first)
		self.assertEqual(
			frappe.db.count(
				"Sarathi Customer Organization", {"company": self.companies[0], "customer": self.customers[0]}
			),
			1,
		)
		self.user("operator")
		with self.assertRaises(frappe.PermissionError):
			associate_customer(self.companies[0], self.customers[0])

	def test_integration_retry_and_invalid_quantity(self):
		payload = {"project": self.projects[0], "request_id": self.token, "planned_qty": 3}
		first = sync_tubepro(payload)
		self.assertEqual(sync_tubepro(payload)["data"]["integration_log"], first["data"]["integration_log"])
		with self.assertRaises(frappe.ValidationError):
			sync_tubepro(dict(payload, planned_qty=4))
		with self.assertRaises(frappe.ValidationError):
			sync_tubepro(dict(payload, request_id=self.token + "bad", completed_qty=-1))
		self.assertEqual(frappe.db.count("Sarathi Machine Integration Log", {"project": self.projects[0]}), 1)

	def test_agent_client_never_escalates_identity_or_runs_scripts(self):
		from sarathi_visibility.api.agent_client import DashboardAgentClient

		client = DashboardAgentClient()
		self.user("manager")
		self.assertEqual(client.get_doc("Project", self.projects[0])["name"], self.projects[0])
		with self.assertRaises(frappe.PermissionError):
			client.get_doc("Project", self.projects[1])
		with self.assertRaises(frappe.PermissionError):
			client.get_doc("GL Entry", "forged")
		with self.assertRaises(frappe.PermissionError):
			client.execute_script("print(1)")
		with self.assertRaises(frappe.PermissionError):
			client.search_docs("Sales Order", {"grand_total": [">", 0]})
		with self.assertRaises(frappe.PermissionError):
			client.create_doc("Company", {"company_name": "forged"})
		self.assertFalse(client.check_permission("Company", "create", user="Administrator")["has_permission"])
		self.user("operator")
		with self.assertRaises(frappe.PermissionError):
			client.search_docs("Job Card")

	def test_agent_cache_is_namespaced_per_user(self):
		from sarathi_visibility.api.agent_chat import _get_agent_state, _persist_agent_state

		sid = "dash003-" + self.token
		self.user("manager")
		state = _get_agent_state(sid, frappe.session.user)
		state.original_request = "private company context"
		_persist_agent_state(sid, state)
		try:
			self.user("owner")
			other = _get_agent_state(sid, frappe.session.user)
			self.assertNotEqual(other.original_request, "private company context")
		finally:
			for user in self.users.values():
				frappe.cache.hdel("sarathi_agent_graph_state", frappe.as_json([user, sid]))
