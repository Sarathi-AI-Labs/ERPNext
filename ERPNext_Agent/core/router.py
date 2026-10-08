"""Skill Router and Intent Classifier for ERPNext AI Agent.

Analyzes user requests, matches DocTypes and domain terminology, classifies action intent,
and routes to the appropriate module skill(s).
"""

import re
from typing import Any, Dict, Set


class SkillRouter:
	"""Classifies user intent and routes execution to appropriate ERPNext Module Skills."""

	# Map DocTypes to their governing module
	DOCTYPE_MODULE_MAP = {
		# Organization
		"company": "Organization",
		"organization": "Organization",
		"abbr": "Organization",
		"abbreviation": "Organization",
		"fiscal year": "Organization",
		"cost center": "Organization",
		"department": "Organization",
		"branch": "Organization",
		"designation": "Organization",
		"currency": "Organization",
		"currency exchange": "Organization",
		"holiday list": "Organization",
		"employee group": "Organization",
		# Stock
		"item": "Stock",
		"item group": "Stock",
		"warehouse": "Stock",
		"bin": "Stock",
		"stock entry": "Stock",
		"delivery note": "Stock",
		"purchase receipt": "Stock",
		"batch": "Stock",
		"serial no": "Stock",
		"stock reconciliation": "Stock",
		"landed cost voucher": "Stock",
		"item price": "Stock",
		"stock ledger": "Stock",
		# Buying
		"supplier": "Buying",
		"supplier group": "Buying",
		"purchase order": "Buying",
		"purchase invoice": "Buying",
		"request for quotation": "Buying",
		"rfq": "Buying",
		"supplier quotation": "Buying",
		"blanket order": "Buying",
		# Selling
		"customer": "Selling",
		"customer group": "Selling",
		"sales order": "Selling",
		"sales invoice": "Selling",
		"quotation": "Selling",
		"lead": "Selling",
		"opportunity": "Selling",
		"sales partner": "Selling",
		# Manufacturing
		"bom": "Manufacturing",
		"bill of materials": "Manufacturing",
		"work order": "Manufacturing",
		"job card": "Manufacturing",
		"operation": "Manufacturing",
		"workstation": "Manufacturing",
		"workstation type": "Manufacturing",
		"production plan": "Manufacturing",
		"routing": "Manufacturing",
		"downtime entry": "Manufacturing",
		# Projects
		"project": "Projects",
		"task": "Projects",
		"timesheet": "Projects",
		"project type": "Projects",
		"activity type": "Projects",
		"project update": "Projects",
		# Subcontracting
		"subcontracting order": "Subcontracting",
		"subcontracting receipt": "Subcontracting",
		"subcontracting bom": "Subcontracting",
		# Quality
		"quality inspection": "Quality",
		"quality inspection parameter": "Quality",
		"quality inspection template": "Quality",
		"quality feedback": "Quality",
		"quality action": "Quality",
		# Accounting
		"journal entry": "Accounting",
		"payment entry": "Accounting",
		"payment request": "Accounting",
		"account": "Accounting",
		"mode of payment": "Accounting",
		"tax category": "Accounting",
		"sales taxes and charges template": "Accounting",
		"purchase taxes and charges template": "Accounting",
		# Assets
		"asset": "Assets",
		"asset category": "Assets",
		"asset movement": "Assets",
		"asset depreciation schedule": "Assets",
		"asset repair": "Assets",
		"asset value adjustment": "Assets",
		# Framework
		"doctype": "Framework",
		"custom field": "Framework",
		"property setter": "Framework",
		"server script": "Framework",
		"client script": "Framework",
		"workflow": "Framework",
		"workflow action": "Framework",
		"print format": "Framework",
		# Users and System
		"user": "Users and System",
		"role": "Users and System",
		"role profile": "Users and System",
		"user permission": "Users and System",
		"system settings": "Users and System",
		"email account": "Users and System",
		"activity log": "Users and System",
		# ERPNext Settings
		"global defaults": "ERPNext Settings",
		"stock settings": "ERPNext Settings",
		"manufacturing settings": "ERPNext Settings",
		"accounts settings": "ERPNext Settings",
		"buying settings": "ERPNext Settings",
		"selling settings": "ERPNext Settings",
	}

	ACTION_PATTERNS = {
		"CREATE": [r"\bcreate\b", r"\badd\b", r"\bnew\b", r"\binsert\b", r"\bmake\b", r"\bsetup\b"],
		"SUBMIT": [r"\bsubmit\b", r"\bpost\b", r"\bfinalize\b", r"\bconfirm\b"],
		"CANCEL": [r"\bcancel\b", r"\bvoid\b", r"\breverse\b"],
		"AMEND": [r"\bamend\b", r"\bcorrect\b"],
		"UPDATE": [r"\bupdate\b", r"\bmodify\b", r"\bchange\b", r"\bedit\b", r"\bset\b"],
		"DELETE": [r"\bdelete\b", r"\bremove\b", r"\bpurge\b"],
		"QUERY": [
			r"\bget\b",
			r"\bfind\b",
			r"\bsearch\b",
			r"\blist\b",
			r"\bshow\b",
			r"\bcheck\b",
			r"\bview\b",
			r"\bread\b",
		],
		"REPORT": [r"\breport\b", r"\banalyze\b", r"\bsummary\b", r"\boverview\b", r"\btrend\b"],
	}

	def route(self, query: str) -> dict[str, Any]:
		"""Classify user intent and identify relevant modules and DocTypes."""
		q_lower = query.lower()

		# 1. Identify Target DocTypes
		matched_doctypes: set[str] = set()
		matched_modules: set[str] = set()

		for term, module in self.DOCTYPE_MODULE_MAP.items():
			pattern = rf"\b{re.escape(term)}s?\b"
			if re.search(pattern, q_lower):
				canonical_dt = "Company" if term in ("abbr", "abbreviation", "organization") else term.title()
				matched_doctypes.add(canonical_dt)
				matched_modules.add(module)

		# 2. Identify Action Intent
		detected_action = "QUERY"  # Default safe action
		for action, patterns in self.ACTION_PATTERNS.items():
			for pat in patterns:
				if re.search(pat, q_lower):
					detected_action = action
					break
			if detected_action != "QUERY":
				break

		# If no explicit module identified, fallback to General or inspect keywords
		if not matched_modules:
			if any(w in q_lower for w in ["manufacture", "production", "assembly"]):
				matched_modules.add("Manufacturing")
			elif any(w in q_lower for w in ["buy", "purchase", "procure"]):
				matched_modules.add("Buying")
			elif any(w in q_lower for w in ["sell", "customer", "sale"]):
				matched_modules.add("Selling")
			elif any(w in q_lower for w in ["inventory", "stock", "warehouse"]):
				matched_modules.add("Stock")
			elif any(w in q_lower for w in ["finance", "ledger", "invoice", "payment", "bank"]):
				matched_modules.add("Accounting")
			elif any(w in q_lower for w in ["project", "gantt", "task"]):
				matched_modules.add("Projects")
			else:
				matched_modules.add("Organization")

		primary_module = sorted(list(matched_modules))[0]

		return {
			"query": query,
			"action": detected_action,
			"primary_module": primary_module,
			"all_modules": sorted(list(matched_modules)),
			"detected_doctypes": sorted(list(matched_doctypes)),
			"is_mutation": detected_action in ("CREATE", "UPDATE", "SUBMIT", "CANCEL", "DELETE"),
			"is_workflow": detected_action in ("SUBMIT", "CANCEL", "AMEND"),
		}
