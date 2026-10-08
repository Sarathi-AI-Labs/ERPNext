"""Cross-Module Dependency Resolver for ERPNext AI Agent.

Calculates prerequisites, validates foreign keys, and builds execution Directed
Acyclic Graphs (DAG) across modules before mutations take place.
"""

from typing import Any, Dict, List

from ERPNext_Agent.tools.client import FrappeClient


class DependencyResolver:
	"""Resolves cross-module entity prerequisites and validates entity references."""

	# Schema dependency mappings (DocType -> list of required parent DocTypes)
	DEPENDENCY_MAP = {
		# Organization
		"Fiscal Year": ["Company"],
		"Cost Center": ["Company"],
		"Department": ["Company"],
		"Holiday List": ["Company"],
		# Stock
		"Item": ["Item Group"],
		"Warehouse": ["Company"],
		"Bin": ["Item", "Warehouse"],
		"Stock Entry": ["Company"],
		"Delivery Note": ["Customer", "Company"],
		"Purchase Receipt": ["Supplier", "Company"],
		# Buying
		"Purchase Order": ["Supplier", "Company"],
		"Purchase Invoice": ["Supplier", "Company"],
		"Request for Quotation": ["Supplier"],
		# Selling
		"Sales Order": ["Customer", "Company"],
		"Sales Invoice": ["Customer", "Company"],
		"Quotation": ["Customer"],
		# Manufacturing
		"BOM": ["Item", "Company"],
		"Work Order": ["Item", "BOM", "Company", "Warehouse"],
		"Job Card": ["Work Order"],
		"Production Plan": ["Company"],
		# Projects
		"Project": ["Company"],
		"Task": ["Project"],
		"Timesheet": ["Company"],
		# Subcontracting
		"Subcontracting Order": ["Supplier", "Company"],
		"Subcontracting Receipt": ["Supplier", "Company"],
		# Quality
		"Quality Inspection": ["Item"],
		# Accounting
		"Journal Entry": ["Company"],
		"Payment Entry": ["Company"],
		"Account": ["Company"],
		# Assets
		"Asset": ["Item", "Company"],
		"Asset Movement": ["Company"],
	}

	def __init__(self, client: FrappeClient):
		self.client = client

	def get_prerequisites(self, doctype: str) -> list[str]:
		"""Return list of prerequisite DocTypes for a given DocType."""
		return self.DEPENDENCY_MAP.get(doctype, [])

	def validate_references(self, doctype: str, doc_values: dict[str, Any]) -> dict[str, Any]:
		"""Verify that all referenced foreign records (Company, Item, Customer, etc.) exist."""
		errors = []

		ref_fields = {
			"company": "Company",
			"item_code": "Item",
			"bom_no": "BOM",
			"customer": "Customer",
			"supplier": "Supplier",
			"project": "Project",
			"cost_center": "Cost Center",
			"warehouse": "Warehouse",
			"wip_warehouse": "Warehouse",
			"fg_warehouse": "Warehouse",
			"set_warehouse": "Warehouse",
			"account": "Account",
		}

		for field, target_doctype in ref_fields.items():
			if doc_values.get(field):
				val = doc_values[field]
				if not self.client.exists(target_doctype, val):
					errors.append(f"Referenced {target_doctype} '{val}' (in field '{field}') does not exist.")

		return {"valid": len(errors) == 0, "errors": errors}

	def plan_creation_order(self, target_doctypes: list[str]) -> list[str]:
		"""Sort doctypes topologically based on dependencies."""
		resolved: list[str] = []
		seen = set()

		def resolve(dt: str):
			if dt in seen:
				return
			seen.add(dt)
			for prereq in self.get_prerequisites(dt):
				if prereq in target_doctypes:
					resolve(prereq)
			resolved.append(dt)

		for dt in target_doctypes:
			resolve(dt)

		return resolved
