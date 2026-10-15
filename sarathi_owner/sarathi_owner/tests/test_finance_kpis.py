"""DASH-009 native-report reconciliation, rollback accounting fixtures and security."""
from decimal import Decimal
import unittest
from unittest.mock import patch

import frappe
from frappe.utils import add_days, today
from erpnext.accounts.utils import get_fiscal_year
from sarathi_owner.api.finance_kpis import get_finance_kpis, native_report, ratio
from sarathi_visibility.tests.test_permissions import PermissionTests


def values(result):
	return {metric["key"]: metric["value"] for metric in result["metrics"]}


class FinanceSecurityTests(PermissionTests):
	def test_finance_direct_capability_and_company_denial(self):
		for user in ("manager", "supervisor", "operator", "unrelated", "finance_only"):
			self.user(user)
			with self.assertRaises(frappe.PermissionError):
				get_finance_kpis({"company": self.companies[0]})
		self.user("owner")
		with self.assertRaises(frappe.PermissionError):
			get_finance_kpis({"company": self.companies[1]})

	def test_record_scoped_owner_cannot_receive_unrestricted_native_totals(self):
		self.user("owner")  # Real native Customer User Permission fixture.
		result = get_finance_kpis({"company": self.companies[0]})
		self.assertTrue(all(metric["value"] is None for metric in result["metrics"]))

	def test_valid_finance_owner_without_record_restrictions(self):
		user = f"dash009-{self.token}@example.invalid"
		frappe.get_doc(dict(doctype="User", email=user, first_name="Finance scope test", send_welcome_email=0,
			roles=[dict(role=role) for role in ("Sarathi Owner", "Accounts Manager", "Accounts User", "Stock User", "Sales User", "Projects User")])).insert()
		frappe.get_doc(dict(doctype="User Permission", user=user, allow="Company", for_value=self.companies[0], apply_to_all_doctypes=1)).insert()
		frappe.set_user(user)
		try:
			result = get_finance_kpis({"company": self.companies[0]})
			self.assertIsNotNone(values(result)["income"])
			self.assertIsNotNone(values(result)["receivables"])
		finally:
			frappe.set_user("Administrator"); frappe.clear_cache(user=user)

	def test_finance_filter_rejection_and_date_order(self):
		for extra in [{"warehouse": "x"}, {"from_date": "2026-4-01"}, {"from_date": "2026-09-01", "to_date": "2026-08-01"}, {"presentation_currency": "USD"}, {"account": "x"}]:
			with self.assertRaises(frappe.ValidationError):
				get_finance_kpis({"company": self.companies[0], **extra})

	def test_customer_filter_does_not_silently_change_profit_or_payables(self):
		result = get_finance_kpis({"company": self.companies[0], "customer": self.customers[0]})
		self.assertIsNone(values(result)["income"])
		self.assertIsNone(values(result)["net_profit"])
		self.assertIsNone(values(result)["payables"])
		self.assertIsNotNone(values(result)["receivables"])

	def test_zero_and_negative_denominator(self):
		self.assertIsNone(ratio(100, 0))
		self.assertEqual(ratio(-20, -100), 20)
		self.assertEqual(ratio(150, 100), 150)

	def test_unexpected_report_failure_never_becomes_zero(self):
		from sarathi_visibility.api.data_helpers import DashboardReadError
		with patch("sarathi_owner.api.finance_kpis.native_report", side_effect=RuntimeError("private SQL")), patch.object(frappe, "log_error"):
			with self.assertRaises(DashboardReadError) as error:
				get_finance_kpis({"company": self.companies[0]})
			self.assertNotIn("private SQL", str(error.exception))

	def test_hidden_gl_amount_field_prevents_derived_totals(self):
		from sarathi_owner.api import finance_kpis
		original = finance_kpis.allowed_fields
		with patch.object(finance_kpis,"allowed_fields",side_effect=lambda dt: original(dt)-{"credit"} if dt=="GL Entry" else original(dt)):
			result=values(get_finance_kpis({"company":self.companies[0]}))
			self.assertIsNone(result["income"])
			self.assertIsNone(result["net_profit"])
			self.assertIsNone(result["receivables"])


class FinanceAccountingTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		frappe.set_user("Administrator")
		frappe.db.savepoint("dash009_accounting")
		cls.company = frappe.get_all("Project", filters={"company": ["is", "set"]}, fields=["company"], limit=1)[0].company
		cls.start = str(get_fiscal_year(today(), company=cls.company)[1])
		cls.end = add_days(cls.start, 90)
		cls.base = get_finance_kpis({"company": cls.company, "from_date": cls.start, "to_date": cls.end})
		company = frappe.get_doc("Company", cls.company)
		cls.receivable = company.default_receivable_account
		cls.payable = company.default_payable_account
		cls.cost_center = company.cost_center
		cls.income = frappe.get_all("Account", filters={"company": cls.company, "root_type": "Income", "is_group": 0, "disabled": 0}, pluck="name", limit=1)[0]
		cls.expense = frappe.get_all("Account", filters={"company": cls.company, "root_type": "Expense", "is_group": 0, "disabled": 0}, pluck="name", limit=1)[0]
		cls.bank = frappe.get_all("Account", filters={"company": cls.company, "account_type": ["in", ["Bank", "Cash"]], "is_group": 0}, pluck="name", limit=1)[0]
		token = frappe.generate_hash(length=8)
		cls.customer = frappe.get_doc(dict(doctype="Customer", customer_name="DASH009 " + token, customer_type="Company")).insert().name
		cls.supplier = frappe.get_doc(dict(doctype="Supplier", supplier_name="DASH009 " + token, supplier_group=frappe.get_all("Supplier Group", filters={"is_group":0}, pluck="name", limit=1)[0], supplier_type="Company")).insert().name
		cls.item = frappe.get_doc(dict(doctype="Item", item_code="DASH009-" + token, item_name="Finance reconciliation fixture", item_group=frappe.get_all("Item Group", filters={"is_group":0}, pluck="name", limit=1)[0], stock_uom=frappe.get_all("UOM", pluck="name", limit=1)[0], is_stock_item=0)).insert().name
		cls.invoice = cls.make_invoice(1000, add_days(cls.start, 10))
		cls.invoice.submit()
		cls.purchase = frappe.get_doc(dict(doctype="Purchase Invoice", company=cls.company, supplier=cls.supplier, set_posting_time=1,
			posting_date=add_days(cls.start, 10), due_date=add_days(cls.start, 40), credit_to=cls.payable,
			items=[dict(item_code=cls.item, qty=1, rate=400, expense_account=cls.expense, cost_center=cls.cost_center)])).insert()
		cls.purchase.submit()
		cls.partial = cls.journal(add_days(cls.start, 20), [
			dict(account=cls.bank, debit_in_account_currency=250),
			dict(account=cls.receivable, party_type="Customer", party=cls.customer, credit_in_account_currency=250, reference_type="Sales Invoice", reference_name=cls.invoice.name)])
		cls.supplier_payment = cls.journal(add_days(cls.start, 20), [
			dict(account=cls.payable, party_type="Supplier", party=cls.supplier, debit_in_account_currency=100, reference_type="Purchase Invoice", reference_name=cls.purchase.name),
			dict(account=cls.bank, credit_in_account_currency=100)])

	@classmethod
	def make_invoice(cls, amount, posting):
		return frappe.get_doc(dict(doctype="Sales Invoice", company=cls.company, customer=cls.customer, set_posting_time=1,
			posting_date=posting, due_date=add_days(posting, 30), debit_to=cls.receivable,
			items=[dict(item_code=cls.item, qty=1, rate=amount, income_account=cls.income, cost_center=cls.cost_center)])).insert()

	@classmethod
	def journal(cls, posting, accounts):
		return frappe.get_doc(dict(doctype="Journal Entry", company=cls.company, posting_date=posting,
			accounts=accounts, user_remark="DASH009 rollback reconciliation fixture")).insert().submit()

	@classmethod
	def tearDownClass(cls):
		frappe.set_user("Administrator")
		frappe.db.rollback(save_point="dash009_accounting")

	def setUp(self):
		frappe.set_user("Administrator"); frappe.db.savepoint("dash009_case")

	def tearDown(self):
		frappe.db.rollback(save_point="dash009_case")

	def result(self, end=None):
		return get_finance_kpis({"company": self.company, "from_date": self.start, "to_date": end or self.end})

	def test_native_invoice_income_expense_and_net_profit(self):
		base, result = values(self.base), values(self.result())
		self.assertAlmostEqual(result["income"] - base["income"], 1000, places=2)
		self.assertAlmostEqual(result["expense"] - base["expense"], 400, places=2)
		self.assertAlmostEqual(result["net_profit"] - base["net_profit"], 600, places=2)
		self.assertAlmostEqual(result["net_margin"], result["net_profit"] / result["income"] * 100, places=8)

	def test_historical_partial_payments_and_supplier_allocations(self):
		before = self.result(add_days(self.start, 15))
		after = self.result(add_days(self.start, 25))
		# Compare only fixture-party native rows, independent of other company activity.
		for source, party, expected_before, expected_after in (("Accounts Receivable",self.customer,1000,750),("Accounts Payable",self.supplier,400,300)):
			def amount(day):
				result = native_report(source, dict(company=self.company, report_date=day, party=[party], ageing_based_on="Due Date", range="30,60,90,120", in_party_currency=0, group_by_party=0))
				return sum(float(row["outstanding"]) for row in result[1] if row.get("voucher_no"))
			self.assertAlmostEqual(amount(add_days(self.start,15)),expected_before,places=2)
			self.assertAlmostEqual(amount(add_days(self.start,25)),expected_after,places=2)

	def test_draft_and_cancelled_invoices_do_not_add_income(self):
		initial = values(self.result())["income"]
		self.make_invoice(777, add_days(self.start, 11))
		cancelled = self.make_invoice(333, add_days(self.start, 12)); cancelled.submit(); cancelled.cancel()
		self.assertAlmostEqual(values(self.result())["income"], initial, places=2)

	def test_return_credit_note_reduces_income_and_receivable(self):
		initial = values(self.result())
		credit = frappe.copy_doc(self.invoice)
		credit.is_return = 1; credit.return_against = self.invoice.name
		credit.posting_date = add_days(self.start,30)
		credit.items[0].qty = -0.1
		credit.insert(); credit.submit()
		result = values(self.result())
		self.assertAlmostEqual(result["income"] - initial["income"], -100, places=2)
		self.assertAlmostEqual(result["receivables"] - initial["receivables"], -100, places=2)

	def test_advance_and_settlement_net_signed_balances(self):
		initial = values(self.result())
		self.journal(add_days(self.start,30), [dict(account=self.bank,debit_in_account_currency=100),dict(account=self.receivable,party_type="Customer",party=self.customer,credit_in_account_currency=100,is_advance="Yes")])
		self.assertAlmostEqual(values(self.result())["receivables"] - initial["receivables"], -100, places=2)
		self.journal(add_days(self.start,31), [dict(account=self.bank,debit_in_account_currency=750),dict(account=self.receivable,party_type="Customer",party=self.customer,credit_in_account_currency=750,reference_type="Sales Invoice",reference_name=self.invoice.name)])
		self.assertAlmostEqual(values(self.result())["receivables"] - initial["receivables"], -850, places=2)

	def test_native_report_reconciliation_same_options(self):
		result = self.result()
		for metric in result["metrics"]:
			if not metric["available"] or metric["unit"] == "%":
				continue
			native = native_report(metric["source"], metric["report_filters"])
			if metric["source"] == "Profit and Loss Statement":
				expected = native[4][{"income":0,"expense":1,"net_profit":2}[metric["key"]]]["value"]
			elif metric["source"] == "Gross Profit":
				expected = [row for row in native[1] if row.get("sales_invoice")=="Total" and row.get("indent") is None][0]["gross_profit"]
			else:
				expected = sum(Decimal(str(row["outstanding"])) for row in native[1] if row.get("voucher_type") and row.get("voucher_no"))
			self.assertAlmostEqual(metric["value"],float(expected),places=2)

	def test_tax_is_not_accounting_income(self):
		taxes = frappe.get_all("Account", filters={"company":self.company,"account_type":"Tax","root_type":"Liability","is_group":0,"disabled":0},pluck="name",limit=1)
		if not taxes:
			self.skipTest("Existing sales tax account required; accounting configuration is not changed")
		initial = values(self.result())
		invoice = self.make_invoice(1000, add_days(self.start,12))
		invoice.append("taxes",dict(charge_type="On Net Total",account_head=taxes[0],description="Rollback fixture tax",rate=10,cost_center=self.cost_center))
		invoice.save(); invoice.submit()
		result = values(self.result())
		self.assertAlmostEqual(result["income"]-initial["income"],1000,places=2)
		self.assertAlmostEqual(result["receivables"]-initial["receivables"],1100,places=2)

	def test_purchase_debit_note_reduces_payables(self):
		initial = values(self.result())
		debit = frappe.copy_doc(self.purchase); debit.is_return=1;debit.return_against=self.purchase.name
		debit.posting_date=add_days(self.start,30);debit.items[0].qty=-0.25
		debit.insert();debit.submit()
		result = values(self.result())
		self.assertAlmostEqual(result["payables"]-initial["payables"],-100,places=2)
		self.assertAlmostEqual(result["expense"]-initial["expense"],-100,places=2)

	def test_posting_and_payment_date_boundaries(self):
		def outstanding(offset):
			report = native_report("Accounts Receivable",dict(company=self.company,report_date=add_days(self.start,offset),party=[self.customer],ageing_based_on="Due Date",range="30,60,90,120",in_party_currency=0,group_by_party=0))
			return sum(float(row["outstanding"]) for row in report[1] if row.get("voucher_no"))
		self.assertAlmostEqual(outstanding(9),0,places=2)
		self.assertAlmostEqual(outstanding(10),1000,places=2)
		self.assertAlmostEqual(outstanding(19),1000,places=2)
		self.assertAlmostEqual(outstanding(20),750,places=2)

	def test_project_dimension_applies_only_to_supported_pnl_metrics(self):
		project = frappe.get_doc(dict(doctype="Project",project_name="DASH009 "+frappe.generate_hash(length=8),company=self.company,customer=self.customer)).insert()
		invoice = self.make_invoice(100,add_days(self.start,12))
		invoice.project=project.name;invoice.items[0].project=project.name;invoice.save();invoice.submit()
		result = values(get_finance_kpis({"company":self.company,"from_date":self.start,"to_date":self.end,"project":project.name}))
		self.assertAlmostEqual(result["income"],100,places=2)
		self.assertIsNone(result["payables"])
		self.assertIsNone(result["gross_profit"])

	def test_foreign_invoice_uses_recorded_base_currency_conversion(self):
		if not frappe.db.exists("Currency","USD"):
			self.skipTest("Existing USD currency master required")
		initial = values(self.result())
		invoice=self.make_invoice(1000,add_days(self.start,12))
		invoice.currency="USD";invoice.conversion_rate=2;invoice.save();invoice.submit()
		result=values(self.result())
		self.assertAlmostEqual(result["income"]-initial["income"],2000,places=2)
		self.assertAlmostEqual(result["receivables"]-initial["receivables"],2000,places=2)


def run():
	suite = unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(FinanceSecurityTests), unittest.defaultTestLoader.loadTestsFromTestCase(FinanceAccountingTests)])
	result = unittest.TextTestRunner(verbosity=2).run(suite)
	frappe.db.rollback()
	if not result.wasSuccessful():
		raise AssertionError("Finance KPI reconciliation tests failed")
	return {"tests":result.testsRun,"skipped":len(result.skipped),"passed":True}
