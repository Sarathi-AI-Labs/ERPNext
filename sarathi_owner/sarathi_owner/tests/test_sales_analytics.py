"""DASH-010 native-controller rollback fixtures and permission regressions."""
import unittest
from unittest.mock import patch

import frappe
from frappe.utils import add_days, today
from sarathi_owner.api.sales_analytics import get_sales_analytics
from sarathi_owner.tests.test_finance_kpis import FinanceAccountingTests
from sarathi_visibility.tests.test_permissions import PermissionTests


class SalesSecurityTests(PermissionTests):
	def test_capabilities_and_forged_company(self):
		for role in ("manager", "supervisor", "operator", "unrelated", "finance_only"):
			self.user(role)
			with self.assertRaises(frappe.PermissionError):
				get_sales_analytics({"company": self.companies[0]})
		self.user("owner")
		with self.assertRaises(frappe.PermissionError):
			get_sales_analytics({"company": self.companies[1]})

	def test_restricted_customer_cannot_receive_complete_aggregates(self):
		self.user("owner")  # Real Customer User Permission, not a mocked role check.
		result = get_sales_analytics({"company": self.companies[0]})
		for key in ("revenue", "backlog"):
			self.assertFalse(result[key]["available"])
			self.assertNotIn("rows", result[key])
		with self.assertRaises(frappe.PermissionError):
			get_sales_analytics({"company":self.companies[0], "customer":self.customers[1]})

	def test_positive_nonadministrator_company_scope(self):
		user = "dash010-" + self.token + "@example.invalid"
		frappe.get_doc(dict(doctype="User", email=user, first_name="Sales scope test", send_welcome_email=0,
			roles=[dict(role=r) for r in ("Sarathi Owner", "Accounts Manager", "Accounts User", "Sales User", "Projects User")])).insert()
		frappe.get_doc(dict(doctype="User Permission", user=user, allow="Company", for_value=self.companies[0], apply_to_all_doctypes=1)).insert()
		frappe.set_user(user)
		try:
			result = get_sales_analytics({"company":self.companies[0]})
			self.assertTrue(result["revenue"]["available"])
			self.assertTrue(result["backlog"]["available"])
		finally:
			frappe.set_user("Administrator"); frappe.clear_cache(user=user)

	def test_filters_limits_dates_and_injection(self):
		for filters in ({"account":"x"}, {"user":"Administrator"}, {"interval":"Weekly"},
			{"top_limit":21}, {"top_limit":True}, {"start":-1}, {"page_length":101}, {"backlog_start":"1 OR 1=1"},
			{"order_status":"Closed"}, {"order_status":"invented"}, {"delivery_from":"2026-10-20","delivery_to":"2026-10-01"},
			{"delivery_from":"2026-2-01"}, {"from_date":"2026-04-01","to_date":"2026-08-01","interval":"Daily"}):
			with self.assertRaises(frappe.ValidationError, msg=str(filters)):
				get_sales_analytics({"company":self.companies[0], **filters})

	def test_hidden_attribution_or_order_fields_fail_closed(self):
		from sarathi_owner.api import sales_analytics
		original = sales_analytics.allowed_fields
		with patch.object(sales_analytics,"allowed_fields",side_effect=lambda dt: original(dt)-{"customer"} if dt=="Sales Invoice" else original(dt)):
			self.assertFalse(get_sales_analytics({"company":self.companies[0]})["revenue"]["available"])
		with patch.object(sales_analytics,"allowed_fields",side_effect=lambda dt: original(dt)-{"base_net_rate"} if dt=="Sales Order Item" else original(dt)):
			self.assertFalse(get_sales_analytics({"company":self.companies[0]})["backlog"]["available"])

	def test_unexpected_failure_is_sanitized_not_zero(self):
		from sarathi_visibility.api.data_helpers import DashboardReadError
		with patch("sarathi_owner.api.sales_analytics.income_groups",side_effect=RuntimeError("private SQL")), patch.object(frappe,"log_error"):
			with self.assertRaises(DashboardReadError) as error:
				get_sales_analytics({"company":self.companies[0]})
			self.assertNotIn("private SQL",str(error.exception))


class SalesAccountingTests(FinanceAccountingTests):
	# Reuse validated finance controller fixtures and retain its tests as regression coverage.
	def analytics(self, **filters):
		return get_sales_analytics({"company":self.company,"from_date":self.start,"to_date":self.end, **filters})

	def invoice_for(self, customer, amount, posting=None, **extra):
		doc = frappe.get_doc(dict(doctype="Sales Invoice",company=self.company,customer=customer,set_posting_time=1,
			posting_date=posting or add_days(self.start,11),due_date=add_days(self.start,40),debit_to=self.receivable,
			items=[dict(item_code=self.item,qty=1,rate=amount,income_account=self.income,cost_center=self.cost_center)], **extra)).insert()
		doc.submit(); return doc

	def customer_fixture(self):
		return frappe.get_doc(dict(doctype="Customer",customer_name="DASH010 "+frappe.generate_hash(length=8),customer_type="Company")).insert().name

	def credit_fixture(self, amount, customer=None, against=None):
		doc=frappe.copy_doc(self.invoice)
		doc.customer=customer or self.customer;doc.is_return=1;doc.return_against=against
		doc.posting_date=add_days(self.start,12)
		doc.items[0].qty=-amount/1000
		doc.insert();doc.submit();return doc

	def order_fixture(self, qty=10, rate=100, submit=True, **extra):
		item_extra = extra.pop("item_extra",{})
		doc = frappe.get_doc(dict(doctype="Sales Order",company=self.company,customer=self.customer,
			transaction_date=add_days(self.start,12),delivery_date=add_days(today(),10),
			items=[dict(item_code=self.item,qty=qty,rate=rate,**{"delivery_date":add_days(today(),10),**item_extra})], **extra)).insert()
		if submit: doc.submit()
		return doc

	def deliver(self, order, qty):
		from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
		doc = make_delivery_note(order.name)
		doc.items[0].qty = qty
		doc.insert(); doc.submit(); order.reload(); return doc

	def test_customer_ranking_ties_pagination_and_nonduplicated_income(self):
		second, third = self.customer_fixture(), self.customer_fixture()
		self.invoice_for(second,2000)
		self.invoice_for(third,2000)
		# Two item rows on one invoice must not multiply its income.
		doc=self.make_invoice(100,add_days(self.start,12)); doc.append("items",dict(item_code=self.item,qty=1,rate=300,income_account=self.income,cost_center=self.cost_center)); doc.save();doc.submit()
		result=self.analytics(top_limit=1,page_length=1)
		info=result["revenue"]
		self.assertTrue(info["available"])
		self.assertEqual(info["customer_total"],5400)
		self.assertEqual(info["rows"][0]["customer"],min(second,third))
		self.assertEqual(len(info["top_customers"]),1)
		self.assertTrue(info["has_next"])
		self.assertEqual(self.analytics(start=1,page_length=1)["revenue"]["rows"][0]["customer"],max(second,third))
		self.assertEqual(sum(row["amount"] for row in info["trend"]),info["included_income"])
		self.assertAlmostEqual(info["rows"][0]["share"],2000/5400*100)

	def test_returns_cancelled_drafts_and_amended_invoices(self):
		draft=self.make_invoice(900,add_days(self.start,12))
		cancelled=self.invoice_for(self.customer,800); cancelled.cancel()
		amended=self.make_invoice(600,add_days(self.start,12)); amended.amended_from=cancelled.name; amended.save(); amended.submit()
		self.credit_fixture(100,against=self.invoice.name)
		result=self.analytics(customer=self.customer)["revenue"]
		self.assertEqual(result["customer_total"],1500)
		self.assertEqual(result["included_income"],sum(row["amount"] for row in result["trend"]))

	def test_unattributed_journal_income_remains_reconcilable(self):
		self.journal(add_days(self.start,13),[dict(account=self.bank,debit_in_account_currency=250),dict(account=self.income,credit_in_account_currency=250,cost_center=self.cost_center)])
		info=self.analytics()["revenue"]
		self.assertEqual(info["unattributed"],250)
		self.assertEqual(info["customer_total"],1000)
		self.assertEqual(info["included_income"],1250)
		self.assertEqual(info["company_accounting_income"],1250)
		selected=self.analytics(customer=self.customer)["revenue"]
		self.assertEqual(selected["included_income"],1000)
		self.assertEqual(selected["unattributed"],0)

	def test_daily_monthly_boundaries_and_measured_empty_period(self):
		self.invoice_for(self.customer,250,add_days(self.start,30))
		result=self.analytics(interval="Daily",to_date=add_days(self.start,31))["revenue"]
		self.assertEqual(len(result["trend"]),32)
		self.assertEqual(result["trend"][0]["amount"],0)
		self.assertEqual(result["trend"][10]["amount"],1000)
		self.assertEqual(result["trend"][30]["amount"],250)
		monthly=self.analytics(to_date=add_days(self.start,31))["revenue"]
		self.assertEqual(sum(row["amount"] for row in monthly["trend"]),1250)
		empty=self.analytics(to_date=add_days(self.start,9))["revenue"]
		self.assertTrue(empty["available"]);self.assertEqual(empty["customer_total"],0)
		self.assertFalse(empty["rows"]);self.assertEqual(sum(row["amount"] for row in empty["trend"]),0)

	def test_zero_and_negative_customer_share(self):
		other=self.customer_fixture(); self.invoice_for(other,100)
		self.credit_fixture(1000,against=self.invoice.name)
		info=self.analytics()["revenue"]
		self.assertEqual(info["customer_total"],100)
		self.assertEqual(next(row for row in info["rows"] if row["customer"]==self.customer)["share"],0)
		self.credit_fixture(100,customer=other)
		info=self.analytics()["revenue"]
		self.assertEqual(info["customer_total"],0)
		self.assertTrue(all(row["share"] is None for row in info["rows"]))

	def test_backlog_partial_delivery_net_discount_and_current_status(self):
		order=self.order_fixture(rate=90,item_extra={"price_list_rate":100,"discount_percentage":10})
		before=self.analytics(customer=self.customer)["backlog"]
		self.assertEqual(before["remaining_value"],900)
		delivery=self.deliver(order,4)
		after=self.analytics(customer=self.customer)["backlog"]
		self.assertEqual(after["remaining_value"],540)
		self.assertEqual(after["quantities"][0]["remaining_qty"],6)
		self.assertEqual(after["rows"][0]["sales_order"],order.name)
		# Native cancellation restores its delivered quantity; no raw status/counter writes.
		delivery.cancel();order.reload()
		self.assertEqual(self.analytics(customer=self.customer)["backlog"]["remaining_value"],900)

	def test_backlog_completed_closed_cancelled_draft_and_held(self):
		self.order_fixture(submit=False)
		cancelled=self.order_fixture();cancelled.cancel()
		closed=self.order_fixture();closed.update_status("Closed")
		completed=self.order_fixture();self.deliver(completed,10)
		held=self.order_fixture();held.update_status("On Hold")
		active=self.order_fixture(qty=2,rate=50)
		info=self.analytics(customer=self.customer)["backlog"]
		self.assertEqual(info["remaining_value"],100)
		self.assertEqual(info["held_value"],1000)
		self.assertEqual(info["open_order_count"],1)
		self.assertEqual(info["held_order_count"],1)
		self.assertEqual({row["sales_order"] for row in info["rows"]},{held.name,active.name})
		selected=self.analytics(customer=self.customer,order_status="On Hold")["backlog"]
		self.assertEqual(selected["remaining_value"],0);self.assertEqual(selected["held_value"],1000)

	def test_backlog_delivery_bounds_pagination_and_overdue(self):
		first=self.order_fixture(); second=self.order_fixture()
		info=self.analytics(customer=self.customer,backlog_page_length=1)["backlog"]
		self.assertTrue(info["has_next"]);self.assertEqual(len(info["rows"]),1)
		self.assertEqual(info["remaining_value"],2000)
		next_page=self.analytics(customer=self.customer,backlog_page_length=1,backlog_start=1)["backlog"]
		self.assertNotEqual(info["rows"][0]["sales_order"],next_page["rows"][0]["sales_order"])
		self.assertEqual(self.analytics(customer=self.customer,delivery_to=today())["backlog"]["remaining_value"],0)
		self.assertEqual(self.analytics(customer=self.customer,delivery_from=add_days(today(),10),delivery_to=add_days(today(),10))["backlog"]["remaining_value"],2000)

	def test_backlog_project_line_fallback_and_unbilled_independence(self):
		project=frappe.get_doc(dict(doctype="Project",project_name="DASH010 "+frappe.generate_hash(length=8),company=self.company,customer=self.customer)).insert()
		order=self.order_fixture(project=project.name)
		from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
		invoice=make_sales_invoice(order.name); invoice.items[0].income_account=self.income;invoice.items[0].cost_center=self.cost_center;invoice.insert();invoice.submit()
		info=self.analytics(customer=self.customer,project=project.name)["backlog"]
		self.assertEqual(info["remaining_value"],1000)  # Fully billed is still undelivered.
		self.assertEqual(len(info["rows"]),1)

	def test_backlog_amended_order_only_active_replacement(self):
		order=self.order_fixture();order.cancel()
		replacement=self.order_fixture(submit=False);replacement.amended_from=order.name;replacement.save();replacement.submit()
		info=self.analytics(customer=self.customer)["backlog"]
		self.assertEqual(info["remaining_value"],1000)
		self.assertEqual([row["sales_order"] for row in info["rows"]],[replacement.name])

	def test_source_reconciliation_failure_is_unavailable(self):
		from sarathi_owner.api import sales_analytics
		original=sales_analytics.native_report
		def changed(*args,**kwargs):
			result=list(original(*args,**kwargs));result[4]=[dict(row) for row in result[4]];result[4][0]["value"]+=1;return result
		with patch.object(sales_analytics,"native_report",side_effect=changed):
			self.assertFalse(self.analytics()["revenue"]["available"])

	def test_signed_negative_customer_share_and_currency(self):
		other=self.customer_fixture()
		self.credit_fixture(100,customer=other)
		info=self.analytics()["revenue"]
		self.assertEqual(info["customer_total"],900)
		self.assertLess(next(row for row in info["rows"] if row["customer"]==other)["share"],0)
		invoice=self.make_invoice(100,add_days(self.start,13));invoice.currency="USD";invoice.conversion_rate=2;invoice.save();invoice.submit()
		info=self.analytics()["revenue"]
		self.assertEqual(info["customer_total"],1100)

	def test_stock_uom_conversion_and_overdue_delivery(self):
		item=frappe.get_doc("Item",self.item)
		other_uom=frappe.get_all("UOM",filters={"name":["!=",item.stock_uom]},pluck="name",limit=1)[0]
		item.append("uoms",dict(uom=other_uom,conversion_factor=2));item.save()
		order=self.order_fixture(item_extra={"uom":other_uom,"conversion_factor":2,"delivery_date":add_days(self.start,13)})
		self.deliver(order,4)
		info=self.analytics(customer=self.customer)["backlog"]
		self.assertEqual(info["quantities"][0]["remaining_qty"],12)
		self.assertEqual(info["overdue_value"],600)
		self.assertEqual(info["rows"][0]["due_state"],"Overdue")

	def test_month_grouping_crosses_calendar_year(self):
		from sarathi_owner.api.sales_analytics import periods
		rows=periods({"from_date":"2026-12-31","to_date":"2027-01-01"},"Monthly")
		self.assertEqual([row["period"] for row in rows],["2026-12","2027-01"])


def run():
	"""Local native fixture suite plus existing homepage and finance regressions."""
	from sarathi_owner.tests.test_homepage import HomepageTests
	from sarathi_owner.tests.test_finance_kpis import FinanceSecurityTests
	suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(cls)
		for cls in (SalesAccountingTests,SalesSecurityTests,HomepageTests,FinanceSecurityTests))
	result=unittest.TextTestRunner(verbosity=2).run(suite)
	frappe.db.rollback()
	if not result.wasSuccessful():
		raise AssertionError("Customer/sales analytics validation failed")
	return {"tests":result.testsRun,"skipped":len(result.skipped),"passed":True}
