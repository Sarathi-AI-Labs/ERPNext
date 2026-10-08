"""Hybrid Intent & Skill Router for ERPNext AI Agent.

Combines deterministic regex/keyword rules, domain entity mapping via SkillRegistry,
live ERPNext metadata, and LLM structured classification into a unified, high-confidence
intent classifier.
"""

from typing import Any, Dict, Optional

from ERPNext_Agent.core.registry import SkillRegistry
from ERPNext_Agent.core.router import SkillRouter
from ERPNext_Agent.llm.gateway import LLMGateway


class HybridRouter:
	"""Combines deterministic domain heuristics with LLM structured reasoning."""

	def __init__(self, registry: SkillRegistry | None = None, llm_gateway: LLMGateway | None = None):
		self.registry = registry or SkillRegistry()
		self.llm = llm_gateway or LLMGateway()
		self.deterministic_router = SkillRouter()

	def route(self, user_message: str) -> dict[str, Any]:
		"""Classify user intent, target module, and DocType(s) with confidence scoring."""
		msg = (user_message or "").strip()
		msg_lower = msg.lower()

		# 1. Deterministic Route
		det_result = self.deterministic_router.route(msg)
		det_dts = det_result.get("detected_doctypes", [])
		det_action = det_result.get("action", "QUERY")
		det_module = det_result.get("primary_module", "Organization")

		# 2. Check for explicit stock or live changes queries
		if any(w in msg_lower for w in ["live changes", "recent changes", "activity", "history"]):
			return {
				"action": "LIVE_CHANGES",
				"primary_module": "Organization",
				"target_doctype": None,
				"detected_doctypes": [],
				"confidence": 1.0,
				"source": "heuristic",
			}

		if (
			any(w in msg_lower for w in ["check stock", "stock in", "inventory", "stock balance"])
			and det_action != "CREATE"
		):
			return {
				"action": "STOCK_QUERY",
				"primary_module": "Stock",
				"target_doctype": "Bin",
				"detected_doctypes": ["Bin"],
				"confidence": 1.0,
				"source": "heuristic",
			}

		# 3. High-Confidence Deterministic Match (DocType explicitly mentioned)
		if det_dts:
			target_dt = det_dts[0]
			module_name = self.registry.get_module_for_doctype(target_dt) or det_module
			return {
				"action": det_action,
				"primary_module": module_name,
				"target_doctype": target_dt,
				"detected_doctypes": det_dts,
				"confidence": 0.95,
				"source": "deterministic",
			}

		# 4. LLM-Assisted Classification (if LLM is available)
		if self.llm.is_available():
			llm_class = self.llm.classify_intent(msg)
			if llm_class and llm_class.target_doctype:
				target_dt = llm_class.target_doctype
				module_name = self.registry.get_module_for_doctype(target_dt) or llm_class.primary_module
				all_dts = [target_dt] + [d for d in llm_class.secondary_doctypes if d != target_dt]
				return {
					"action": llm_class.action,
					"primary_module": module_name,
					"target_doctype": target_dt,
					"detected_doctypes": all_dts,
					"confidence": llm_class.confidence,
					"source": "llm",
				}

		# 5. Low-confidence fallback
		return {
			"action": det_action,
			"primary_module": det_module,
			"target_doctype": None,
			"detected_doctypes": [],
			"confidence": 0.4,
			"source": "fallback",
		}
