"""DASH-004 definition/evidence checks. Standard-library unittest, no site writes.

Run from repository root with:
python -m unittest discover -s sarathi_visibility/sarathi_visibility/tests -p test_kpi_dictionary.py -v
These checks validate the specification and captured evidence, not unimplemented APIs.
"""

import json
import math
import re
import unittest
from datetime import date
from pathlib import Path


class KPIDictionaryTests(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		docs = Path(__file__).resolve().parents[3] / "docs"
		cls.registry = json.loads((docs / "dashboard-kpi-dictionary.json").read_text(encoding="utf-8"))
		cls.evidence = json.loads((docs / "dashboard-kpi-validation.json").read_text(encoding="utf-8"))
		cls.document = (docs / "dashboard-kpi-dictionary.md").read_text(encoding="utf-8")
		cls.kpis = {k["id"]: k for k in cls.registry["kpis"]}

	def test_each_definition_has_all_required_contract_attributes(self):
		required = {
			"id",
			"name",
			"dashboards",
			"section",
			"business_purpose",
			"definition",
			"formula",
			"numerator",
			"denominator",
			"sources",
			"record_rules",
			"docstatus",
			"date_basis",
			"filters",
			"currency_rounding",
			"missing_empty_zero",
			"permissions",
			"refresh",
			"drill_down",
			"validation",
			"limitations",
			"implementation_status",
		}
		for kpi in self.kpis.values():
			with self.subTest(kpi=kpi["id"]):
				self.assertEqual(set(kpi), required)
				self.assertTrue(all(kpi[key] for key in required))
				self.assertIn(
					kpi["implementation_status"], {"verified", "proposed", "blocked", "not configured"}
				)
				self.assertRegex(kpi["id"], r"^[A-Z]+-\d{3}$")

	def test_unique_ids_cover_all_dashboard_personas(self):
		self.assertEqual(len(self.kpis), len(self.registry["kpis"]))
		self.assertGreaterEqual(len(self.kpis), 60)
		self.assertEqual(
			{role for kpi in self.kpis.values() for role in kpi["dashboards"]},
			{"Owner", "Production", "Shop-floor supervisor", "Shop-floor operator"},
		)

	def test_formula_dependencies_resolve_to_shared_definitions(self):
		pattern = r"\b(?:FIN|AR|AP|SALES|PROJ|MFG|OPS|JOB|INV|QUAL|WS|SUB|ALERT|CAT)-\d{3}\b"
		for kpi in self.kpis.values():
			for ref in re.findall(pattern, " ".join(kpi[k] for k in ("formula", "numerator", "denominator"))):
				with self.subTest(kpi=kpi["id"], dependency=ref):
					self.assertIn(ref, self.kpis)

	def test_declared_fields_exist_in_installed_schema_evidence(self):
		for kpi in self.kpis.values():
			for doctype, fields in kpi["sources"].items():
				with self.subTest(kpi=kpi["id"], doctype=doctype):
					source = self.evidence["source_metadata"][doctype]
					self.assertTrue(source["exists"])
					self.assertEqual(source["missing_fields"], [])
					self.assertLessEqual(set(fields), set(source["fields"]))
		# Guard the actual schema mismatch that legacy code must not repeat.
		budget_fields = self.kpis["FIN-009"]["sources"]["Budget"]
		self.assertNotIn("fiscal_year", budget_fields)
		self.assertIn("from_fiscal_year", budget_fields)
		self.assertIn("Budget Distribution", self.kpis["FIN-009"]["sources"])

	def test_native_comparison_evidence_is_complete_and_consistent(self):
		checks = self.evidence["checks"]
		self.assertEqual(len(checks), 12)
		for check in checks:
			with self.subTest(check=check["id"]):
				self.assertEqual(check["status"], "verified")
				self.assertGreater(check["records"], 0)
				self.assertTrue(math.isclose(check["expected"], check["actual"], abs_tol=0.01))
				self.assertTrue(
					math.isclose(check["actual"] - check["expected"], check["difference"], abs_tol=0.000001)
				)
				self.assertLessEqual(set(check["kpi_ids"]), set(self.kpis))
		self.assertEqual(self.evidence["versions"], self.registry["runtime_versions"])
		date.fromisoformat(self.evidence["scope"]["as_of"])
		self.assertIn("Administrator", self.evidence["scope"]["actor"])
		self.assertTrue(self.evidence["not_exercised"])

	def test_missing_operational_sources_are_not_claimed_as_verified(self):
		for identifier in (
			"JOB-006",
			"JOB-008",
			"JOB-010",
			"OPS-001",
			"WS-002",
			"WS-004",
			"SUB-001",
			"ALERT-005",
		):
			self.assertEqual(self.kpis[identifier]["implementation_status"], "not configured")
		for identifier in ("JOB-007", "JOB-012", "JOB-013", "INV-004", "INV-009", "PROJ-005"):
			self.assertEqual(self.kpis[identifier]["implementation_status"], "blocked")
		self.assertIsNone(self.evidence["configuration_gaps"]["Shift Type"])

	def test_rendered_document_contains_each_complete_definition(self):
		for kpi in self.kpis.values():
			self.assertEqual(self.document.count("### " + kpi["id"] + " — " + kpi["name"] + "\n"), 1)
		for label in (
			"Numerator",
			"Denominator",
			"Required permissions",
			"Refresh and freshness",
			"Missing/empty/zero handling",
		):
			self.assertEqual(self.document.count("| " + label + " |"), len(self.kpis))
		self.assertIn("not dashboard or financial release approval", self.document)
		self.assertIn("Scenario catalogue", self.document)


if __name__ == "__main__":
	unittest.main()
