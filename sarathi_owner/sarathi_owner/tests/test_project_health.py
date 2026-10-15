"""DASH-011 native Project/Task and delivery lifecycle rollback fixtures."""
from datetime import timedelta
import unittest
from unittest.mock import patch

import frappe
from frappe.utils import add_days, getdate, now_datetime, today
from sarathi_owner.api.project_health import get_project_delivery_health, classify_project
from sarathi_owner.tests.test_sales_analytics import SalesAccountingTests
from sarathi_visibility.tests.test_permissions import PermissionTests


class ProjectSecurityTests(PermissionTests):
	def setUp(self):
		frappe.db.savepoint("dash011_security_case")

	def tearDown(self):
		frappe.set_user("Administrator");frappe.db.rollback(save_point="dash011_security_case")
		for user in self.users.values():frappe.clear_cache(user=user)

	def test_health_capabilities_company_and_project_denial(self):
		for user in ("manager","operator","supervisor","unrelated","finance_only"):
			self.user(user)
			with self.assertRaises(frappe.PermissionError):get_project_delivery_health({"company":self.companies[0]})
		self.user("owner")
		for filters in ({"company":self.companies[1]},{"company":self.companies[0],"project":self.projects[1]},{"company":self.companies[0],"customer":self.customers[1]}):
			with self.assertRaises(frappe.PermissionError):get_project_delivery_health(filters)

	def test_customer_limited_owner_gets_native_project_subset(self):
		self.user("owner")
		result=get_project_delivery_health({"company":self.companies[0]})
		self.assertTrue(result["projects"]["available"])
		self.assertEqual([row["name"] for row in result["projects"]["rows"]],[self.projects[0]])
		self.assertEqual(result["projects"]["counts"]["total"],1)
		self.assertFalse(result["deliveries"]["available"])

	def test_task_permissions_do_not_expose_hidden_rows_or_counts(self):
		visible=frappe.get_doc(dict(doctype="Task",subject="DASH011 visible",project=self.projects[0],company=self.companies[0],exp_end_date=add_days(today(),-1))).insert()
		hidden=frappe.get_doc(dict(doctype="Task",subject="DASH011 hidden",project=self.projects[0],company=self.companies[0],exp_end_date=add_days(today(),-2))).insert()
		frappe.get_doc(dict(doctype="User Permission",user=self.users["owner"],allow="Task",for_value=visible.name,apply_to_all_doctypes=1)).insert()
		self.user("owner")
		result=get_project_delivery_health({"company":self.companies[0],"task_view":"All incomplete"})
		tasks=result["projects"]["tasks"]
		self.assertTrue(tasks["available"])
		self.assertEqual([row["name"] for row in tasks["rows"]],[visible.name])
		self.assertEqual(tasks["counts"]["overdue_tasks"],1)
		self.assertNotIn(hidden.name,str(result))

	def test_hidden_task_field_keeps_recorded_project_progress(self):
		from sarathi_owner.api import project_health
		original=project_health.allowed_fields
		with patch.object(project_health,"allowed_fields",side_effect=lambda dt:original(dt)-{"exp_end_date"} if dt=="Task" else original(dt)):
			result=get_project_delivery_health({"company":self.companies[0],"project":self.projects[0]})
			self.assertTrue(result["projects"]["available"])
			self.assertFalse(result["projects"]["tasks"]["available"])
			self.assertIsNotNone(result["projects"]["rows"][0]["progress"])
			self.assertTrue(result["projects"]["rows"][0]["progress_warnings"])

	def test_strict_health_filters_and_bounds(self):
		for filters in ({"user":"Administrator"},{"doctype":"Task"},{"reference_at":"2026-02-30T10:00"},{"reference_at":"2026-10-14T10:00:00+05:30"},
			{"review_days":91},{"review_days":True},{"review_days":-1},{"project_status":"Closed"},{"project_health":"On track"},
			{"task_view":"Blocked"},{"project_page_length":101},{"task_start":-1},{"delivery_view":"Forecast"},{"delivery_from":"2026-10-20","delivery_to":"2026-10-01"}):
			with self.assertRaises(frappe.ValidationError,msg=str(filters)):get_project_delivery_health({"company":self.companies[0],**filters})

	def test_read_failure_is_sanitized(self):
		from sarathi_visibility.api.data_helpers import DashboardReadError
		with patch("sarathi_owner.api.project_health.projects",side_effect=RuntimeError("private SQL")),patch.object(frappe,"log_error"):
			with self.assertRaises(DashboardReadError) as error:get_project_delivery_health({"company":self.companies[0]})
			self.assertNotIn("private SQL",str(error.exception))


class ProjectNativeTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.set_user("Administrator");frappe.db.savepoint("dash011_projects")
		cls.company=frappe.get_all("Project",filters={"company":["is","set"]},fields=["company"],limit=1)[0].company
		cls.customer=frappe.get_doc(dict(doctype="Customer",customer_name="DASH011 "+frappe.generate_hash(length=8),customer_type="Company")).insert().name
		cls.ref=now_datetime().replace(microsecond=0)

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator");frappe.db.rollback(save_point="dash011_projects")

	def setUp(self):
		frappe.set_user("Administrator");frappe.db.savepoint("dash011_project_case")

	def tearDown(self):frappe.db.rollback(save_point="dash011_project_case")

	def project(self, **extra):
		values=dict(doctype="Project",project_name="DASH011 "+frappe.generate_hash(length=8),company=self.company,customer=self.customer,
			percent_complete_method="Manual",percent_complete=20)
		values.update(extra);return frappe.get_doc(values).insert()

	def task(self, project, **extra):
		values=dict(doctype="Task",subject="DASH011 "+frappe.generate_hash(length=8),project=project.name,company=self.company,status="Working",progress=20)
		values.update(extra);return frappe.get_doc(values).insert()

	def result(self, **extra):
		return get_project_delivery_health({"company":self.company,"customer":self.customer,"reference_at":str(self.ref),**extra})

	def test_native_project_status_counts_and_date_boundaries(self):
		self.project(expected_end_date=add_days(today(),-1))
		self.project(expected_end_date=today())
		self.project(expected_end_date=add_days(today(),7))
		self.project(expected_end_date=add_days(today(),8))
		self.project(status="On hold",expected_end_date=add_days(today(),9))
		self.project(status="Completed",expected_end_date=add_days(today(),-10))
		self.project(status="Cancelled",expected_end_date=add_days(today(),-10))
		self.project()
		result=self.result()["projects"]
		self.assertEqual(result["counts"],dict(total=8,active=6,completed=1,cancelled=1,overdue=1,due_soon=2,held=1,at_risk=1,unknown=1))
		self.assertEqual(sum(result["health_partition"].values()),8)
		self.assertEqual(len(self.result(project_health="Overdue")["projects"]["rows"]),1)
		self.assertEqual(self.result(project_status="Completed")["projects"]["counts"]["overdue"],0)
		self.assertEqual(self.result(review_days=0)["projects"]["counts"]["due_soon"],1)

	def test_manual_native_and_no_task_progress(self):
		manual=self.project(percent_complete=37.125)
		empty=self.project(percent_complete_method="Task Completion")
		result=self.result()["projects"]
		rows={row["name"]:row for row in result["rows"]}
		self.assertEqual(rows[manual.name]["progress"],manual.percent_complete)
		self.assertEqual(rows[empty.name]["progress"],0)
		self.assertTrue(rows[empty.name]["progress_warnings"])

	def test_native_task_completion_includes_cancelled_tasks(self):
		project=self.project(percent_complete_method="Task Completion")
		self.task(project,status="Completed")
		self.task(project,status="Cancelled")
		self.task(project,status="Working")
		project.reload()
		row=self.result(project=project.name)["projects"]["rows"][0]
		self.assertEqual(row["progress"],project.percent_complete)
		self.assertAlmostEqual(row["progress"],66.67,places=2)
		self.assertEqual(row["task_coverage"]["visible_tasks"],3)

	def test_native_progress_and_weight_methods_no_new_average(self):
		progress=self.project(percent_complete_method="Task Progress")
		self.task(progress,progress=20);self.task(progress,progress=60)
		weighted=self.project(percent_complete_method="Task Weight")
		self.task(weighted,progress=20,task_weight=25);self.task(weighted,progress=60,task_weight=75)
		rows={row["name"]:row for row in self.result()["projects"]["rows"]}
		self.assertEqual(rows[progress.name]["progress"],40)
		self.assertEqual(rows[weighted.name]["progress"],50)
		self.assertEqual(len(rows),2)  # Four Tasks must not multiply Project counts.

	def test_milestones_task_timestamp_boundaries_and_terminal_exclusion(self):
		project=self.project(expected_end_date=add_days(today(),20))
		self.task(project,exp_end_date=self.ref-timedelta(seconds=1),is_milestone=1)
		self.task(project,exp_end_date=self.ref,is_milestone=1)
		self.task(project,exp_end_date=self.ref+timedelta(days=7),is_milestone=1)
		self.task(project,exp_end_date=self.ref+timedelta(days=7,seconds=1))
		self.task(project,status="Completed",exp_end_date=self.ref-timedelta(days=1))
		self.task(project,status="Cancelled",exp_end_date=self.ref-timedelta(days=1))
		self.task(project)
		result=self.result()["projects"]
		self.assertEqual(result["rows"][0]["health"],"At risk")
		self.assertEqual(result["tasks"]["counts"],dict(overdue_tasks=1,due_soon_tasks=2,overdue_milestones=1,due_soon_milestones=2,unknown_dates=1))
		self.assertEqual(len(self.result(task_view="Milestones")["projects"]["tasks"]["rows"]),3)

	def test_project_and_task_pagination_and_customer_scope(self):
		for _ in range(3):
			p=self.project();self.task(p,exp_end_date=self.ref-timedelta(days=1))
		result=self.result(project_page_length=1,task_page_length=1)["projects"]
		self.assertEqual(result["counts"]["total"],3);self.assertTrue(result["has_next"])
		self.assertTrue(result["tasks"]["has_next"])
		second=self.result(project_page_length=1,project_start=1)["projects"]
		self.assertNotEqual(result["rows"][0]["name"],second["rows"][0]["name"])
		unlinked=self.project(customer=None)
		self.assertNotIn(unlinked.name,str(self.result()))

	def test_project_cohort_is_expected_start_not_completion(self):
		project=self.project(expected_start_date=add_days(today(),-10),expected_end_date=add_days(today(),20))
		self.assertEqual(self.result(from_date=add_days(today(),-10),to_date=add_days(today(),-10))["projects"]["counts"]["total"],1)
		self.assertEqual(self.result(from_date=today())["projects"]["counts"]["total"],0)

	def test_invalid_legacy_progress_schedule_and_unknown_status_safe(self):
		project=self.project();row=frappe._dict(project.as_dict());row.expected_start_date=add_days(today(),2);row.expected_end_date=today();row.percent_complete=150
		result=classify_project(row,self.ref,7,None)
		self.assertEqual(result["health"],"Unknown");self.assertIsNone(result["progress"])
		row.status="Unmapped custom status"
		self.assertEqual(classify_project(row,self.ref,7,None)["health"],"Unknown")


class ProjectDeliveryTests(SalesAccountingTests):
	# Existing native sales/finance tests are intentionally retained as regression coverage.
	def health(self, **extra):
		return get_project_delivery_health({"company":self.company,"customer":self.customer,**extra})["deliveries"]

	def test_health_partial_full_delivery_and_cancellation(self):
		order=self.order_fixture()
		self.assertEqual(self.health()["counts"]["open_orders"],1)
		delivery=self.deliver(order,4)
		result=self.health()
		self.assertEqual(result["counts"]["partially_delivered_orders"],1)
		self.assertEqual(result["rows"][0]["remaining_qty"],6)
		delivery.cancel()
		self.assertEqual(self.health()["counts"]["partially_delivered_orders"],0)
		self.deliver(order,10)
		self.assertEqual(self.health()["counts"]["open_orders"],0)

	def test_multiple_delivery_dates_distinct_order_counts_and_hold(self):
		order=self.order_fixture(submit=False,item_extra={"delivery_date":add_days(today(),-1)})
		order.append("items",dict(item_code=self.item,qty=2,rate=100,delivery_date=today()));order.save();order.submit()
		held=self.order_fixture();held.update_status("On Hold")
		result=self.health()
		self.assertEqual(result["counts"]["open_orders"],1)
		self.assertEqual(result["counts"]["overdue_orders"],1)
		self.assertEqual(result["counts"]["due_soon_orders"],1)
		self.assertEqual(result["counts"]["held_orders"],1)
		self.assertEqual(len(self.health(delivery_view="Overdue")["rows"]),1)

	def test_delivery_project_fallback_line_override_and_cohort(self):
		first=frappe.get_doc(dict(doctype="Project",project_name="DASH011 "+frappe.generate_hash(length=8),company=self.company,customer=self.customer)).insert()
		second=frappe.get_doc(dict(doctype="Project",project_name="DASH011 "+frappe.generate_hash(length=8),company=self.company,customer=self.customer)).insert()
		order=self.order_fixture(project=first.name,item_extra={"project":second.name})
		self.assertEqual(self.health(project=second.name)["counts"]["open_orders"],1)
		self.assertEqual(self.health(project=first.name)["counts"]["open_orders"],0)
		self.assertEqual(self.health(from_date=today())["counts"]["open_orders"],0)
		self.assertEqual(self.health(from_date=add_days(self.start,12),to_date=add_days(self.start,12))["counts"]["open_orders"],1)

	def test_delivery_excluded_and_amended_order_health(self):
		self.order_fixture(submit=False)
		closed=self.order_fixture();closed.update_status("Closed")
		cancelled=self.order_fixture();cancelled.cancel()
		replacement=self.order_fixture(submit=False);replacement.amended_from=cancelled.name;replacement.save();replacement.submit()
		result=self.health(health_delivery_page_length=1)
		self.assertEqual(result["counts"]["open_orders"],1)
		self.assertEqual(result["rows"][0]["sales_order"],replacement.name)
		self.assertFalse(result["has_next"])
		self.assertNotIn("remaining_value",str(result))

	def test_missing_delivery_date_classification_without_record_mutation(self):
		from sarathi_owner.api.project_health import delivery_health
		# Native Sales Order validation requires dates: verify legacy missing data
		# classification without corrupting transactions or bypassing validation.
		row=frappe._dict(status="To Deliver and Bill",delivery_date=None)
		self.assertEqual(delivery_health(row,now_datetime(),7),"Unknown")
		row.delivery_date="invalid legacy date"
		self.assertEqual(delivery_health(row,now_datetime(),7),"Unknown")


def run():
	from sarathi_owner.tests.test_homepage import HomepageTests
	from sarathi_owner.tests.test_finance_kpis import FinanceSecurityTests
	suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls) for cls in (ProjectNativeTests,ProjectSecurityTests,ProjectDeliveryTests,HomepageTests,FinanceSecurityTests))
	result=unittest.TextTestRunner(verbosity=2).run(suite);frappe.db.rollback()
	if not result.wasSuccessful():raise AssertionError("Project and delivery health tests failed")
	return {"tests":result.testsRun,"skipped":len(result.skipped),"passed":True}
