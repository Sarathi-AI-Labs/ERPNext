"""Skill Registry for ERPNext AI Agent.

Maintains an indexed catalog of the 13 ERPNext domain modules and their submodules,
enabling zero-latency mapping from DocTypes to Skill paths without loading full
markdown files into context unnecessarily.
"""

import os
from typing import Any, Dict, List, Optional


class SkillRegistry:
	"""Central registry of all 13 ERPNext module skills and their sub-sections."""

	# Explicit mapping of ERPNext DocTypes to (Module, Submodule Directory Name)
	DOCTYPE_TO_SKILL = {
		# 1. Organization
		"Company": ("Organization", "Company"),
		"Department": ("Organization", "Department"),
		"Branch": ("Organization", "Branch"),
		"Letter Head": ("Organization", "Letter Head"),
		"Role Permissions": ("Organization", "Role Permissions"),
		"Email Account": ("Organization", "Email Account"),
		"Sarathi Customer Organization": ("Organization", "Sarathi Customer Organization"),
		"Fiscal Year": ("Organization", "Company"),
		"Cost Center": ("Organization", "Company"),
		# 2. Projects
		"Project": ("Projects", "Project"),
		"Task": ("Projects", "Task"),
		"Timesheet": ("Projects", "Timesheet"),
		"Project Type": ("Projects", "Setup"),
		"Activity Type": ("Projects", "Setup"),
		# 3. Selling
		"Customer": ("Selling", "Items and Pricing"),
		"Customer Group": ("Selling", "Setup"),
		"Quotation": ("Selling", "Quotation"),
		"Sales Order": ("Selling", "Sales Order"),
		"Sales Invoice": ("Selling", "Sales Invoice"),
		"POS Profile": ("Selling", "POS"),
		# 4. Buying
		"Supplier": ("Buying", "Setup"),
		"Supplier Group": ("Buying", "Setup"),
		"Purchase Order": ("Buying", "Purchase Order"),
		"Purchase Invoice": ("Buying", "Purchase Invoice"),
		"Material Request": ("Buying", "Material Request"),
		"Request for Quotation": ("Buying", "Request for Quotation"),
		"Supplier Quotation": ("Buying", "Supplier Quotation"),
		# 5. Stock
		"Item": ("Stock", "Setup"),
		"Item Group": ("Stock", "Setup"),
		"Warehouse": ("Stock", "Setup"),
		"Stock Entry": ("Stock", "Stock Entry"),
		"Delivery Note": ("Stock", "Delivery Note"),
		"Purchase Receipt": ("Stock", "Purchase Receipt"),
		"Pick List": ("Stock", "Pick List"),
		"Bin": ("Stock", "Tools"),
		# 6. Manufacturing
		"BOM": ("Manufacturing", "BOM"),
		"Work Order": ("Manufacturing", "Work Order"),
		"Job Card": ("Manufacturing", "Job Card"),
		"Workstation": ("Manufacturing", "Setup"),
		"Operation": ("Manufacturing", "Setup"),
		# 7. Accounting
		"Account": ("Accounting", "Accounts Setup"),
		"Journal Entry": ("Accounting", "Invoicing"),
		"Payment Entry": ("Accounting", "Payments"),
		"Tax Category": ("Accounting", "Taxes"),
		# 8. Quality
		"Quality Inspection": ("Quality", "Quality Inspection"),
		"Quality Goal": ("Quality", "Quality Goals and Reviews"),
		"Non Conformance": ("Quality", "Non Conformance"),
		# 9. Assets
		"Asset": ("Assets", "Asset"),
		"Asset Category": ("Assets", "Setup"),
		"Asset Movement": ("Assets", "Asset Movement"),
		# 10. Subcontracting
		"Subcontracting Order": ("Subcontracting", "Inward Order"),
		"Subcontracting Receipt": ("Subcontracting", "Outward Order"),
		"Subcontracting BOM": ("Subcontracting", "Subcontracting BOM"),
		# 11. ERPNext Settings
		"Global Defaults": ("ERPNext Settings", "Global Defaults"),
		"System Settings": ("ERPNext Settings", "System Settings"),
		"Stock Settings": ("ERPNext Settings", "Stock Settings"),
		# 12. Framework
		"DocType": ("Framework", "DocType"),
		"Custom Field": ("Framework", "Customization"),
		"Server Script": ("Framework", "Server Scripts"),
		"Client Script": ("Framework", "Client Scripts"),
		# 13. Users and System
		"User": ("Users and System", "Users"),
		"Role": ("Users and System", "Roles"),
		"User Permission": ("Users and System", "Permissions"),
	}

	MODULES = [
		"Organization",
		"Assets",
		"Buying",
		"Manufacturing",
		"Projects",
		"Quality",
		"Selling",
		"Subcontracting",
		"Accounting",
		"Stock",
		"ERPNext Settings",
		"Framework",
		"Users and System",
	]

	def __init__(self, agent_dir: str | None = None):
		self.agent_dir = agent_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

	def get_module_for_doctype(self, doctype: str) -> str | None:
		"""Return primary governing module for a DocType."""
		dt_title = doctype.strip().title()
		if dt_title in self.DOCTYPE_TO_SKILL:
			return self.DOCTYPE_TO_SKILL[dt_title][0]
		for dt, (mod, _) in self.DOCTYPE_TO_SKILL.items():
			if dt.lower() == doctype.strip().lower():
				return mod
		return None

	def get_section_for_doctype(self, doctype: str) -> tuple[str, str] | None:
		"""Return (Module, Section) tuple for a DocType."""
		dt_title = doctype.strip().title()
		if dt_title in self.DOCTYPE_TO_SKILL:
			return self.DOCTYPE_TO_SKILL[dt_title]
		for dt, mapping in self.DOCTYPE_TO_SKILL.items():
			if dt.lower() == doctype.strip().lower():
				return mapping
		return None

	def list_modules(self) -> list[str]:
		"""Return list of all 13 modules."""
		return list(self.MODULES)

	def get_module_path(self, module_name: str) -> str:
		"""Return absolute filesystem path to module folder."""
		return os.path.join(self.agent_dir, module_name)

	def get_module_meta(self, module_name: str) -> dict[str, Any] | None:
		"""Return module metadata including sub-sections and paths."""
		if module_name not in self.MODULES:
			return None
		mod_path = self.get_module_path(module_name)
		sections = {}
		if os.path.exists(mod_path):
			for item in os.listdir(mod_path):
				sub_path = os.path.join(mod_path, item)
				if os.path.isdir(sub_path) and not item.startswith("."):
					sections[item] = sub_path
		return {"module": module_name, "path": mod_path, "sections": sections}
