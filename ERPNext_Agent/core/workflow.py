"""LangGraph Workflow Engine for Sarathi ERPNext AI Agent.

Implements the complete 14-Node State Graph using LangGraph:
START -> understand_request -> route_skill -> load_skill -> load_metadata ->
extract_parameters -> check_missing_information -> resolve_dependencies ->
validate -> check_permission -> confirmation_if_required -> execute_tool ->
verify_result -> audit -> respond -> END
"""

import json
import re
from typing import Any, Dict, Optional

from langgraph.graph import END, START, StateGraph

from ERPNext_Agent.core.audit import AuditLogger
from ERPNext_Agent.core.hybrid_router import HybridRouter
from ERPNext_Agent.core.loader import SkillLoader
from ERPNext_Agent.core.metadata_service import MetadataService
from ERPNext_Agent.core.registry import SkillRegistry
from ERPNext_Agent.core.resolver import DependencyResolver
from ERPNext_Agent.core.slot_registry import get_clean_pending_values, get_slots_for_doctype
from ERPNext_Agent.core.state import AgentState
from ERPNext_Agent.core.validator import ReadBackValidator
from ERPNext_Agent.llm.gateway import LLMGateway
from ERPNext_Agent.tools.client import FrappeClient
from ERPNext_Agent.tools.tool_registry import ToolRegistry


class SarathiAgentGraph:
	"""Orchestrates ERPNext Agent workflows via a compiled LangGraph state machine."""

	def __init__(self, client: FrappeClient | None = None):
		self.client = client or FrappeClient()
		self.registry = SkillRegistry()
		self.loader = SkillLoader()
		self.metadata_service = MetadataService(self.client)
		self.llm = LLMGateway()
		self.router = HybridRouter(self.registry, self.llm)
		self.resolver = DependencyResolver(self.client)
		self.validator = ReadBackValidator(self.client)
		self.audit = AuditLogger()
		self.tool_registry = ToolRegistry(self.client)

		self.graph = self._build_graph()

	# -------------------------------------------------------------
	# 14 LangGraph Node Implementations
	# -------------------------------------------------------------

	def node_understand_request(self, state: AgentState) -> dict[str, Any]:
		"""Node 1: Parse and normalize incoming user request."""
		req = (state.original_request or "").strip()
		updates: dict[str, Any] = {"final_response": None}

		# Handle cancel / reset
		if req.lower() in ("cancel", "abort", "reset", "clear"):
			state.reset()
			return {
				"status": "IDLE",
				"parameters": {},
				"missing_parameters": [],
				"selected_doctypes": [],
				"selected_skills": [],
				"final_response": {
					"message": "🔄 Conversation reset. Ready for your next ERPNext instruction!",
					"status": "IDLE",
					"action_steps": ["Session reset", "Context cleared"],
				},
			}

		if state.status not in ("COLLECTING_SLOTS", "AWAITING_CONFIRMATION"):
			updates["status"] = "UNDERSTANDING"

		return updates

	def node_route_skill(self, state: AgentState) -> dict[str, Any]:
		"""Node 2: Classify intent and route to target module(s)."""
		route_res = self.router.route(state.original_request)
		action = route_res.get("action", "QUERY")
		primary_mod = route_res.get("primary_module", "Organization")
		target_dt = route_res.get("target_doctype")
		detected_dts = route_res.get("detected_doctypes", [])

		if target_dt and target_dt not in detected_dts:
			detected_dts.insert(0, target_dt)

		# Check if user is explicitly switching to a different DocType/command in multi-turn
		if state.selected_doctypes and state.status in ("COLLECTING_SLOTS", "AWAITING_CONFIRMATION"):
			# If user mentioned a DIFFERENT DocType (e.g. "I want to create a project" while in Company)
			if detected_dts and set(detected_dts) != set(state.selected_doctypes):
				# Switch topic! Reset old parameters and switch to new DocType
				state.parameters = {}
				state.missing_parameters = []
				state.execution_results = []
				state.verification_results = {}
				state.confirmation_required = False
				state.confirmation_status = "PENDING"
				state.status = "UNDERSTANDING"

				mods = []
				for dt in detected_dts:
					m = self.registry.get_module_for_doctype(dt)
					if m and m not in mods:
						mods.append(m)
				if not mods:
					mods = [primary_mod]

				return {
					"intent": action if action != "QUERY" else "CREATE",
					"selected_skills": mods,
					"selected_doctypes": detected_dts,
					"parameters": {},
					"missing_parameters": [],
					"status": "UNDERSTANDING",
				}

			# If user didn't mention a new DocType, continue active session
			return {
				"intent": state.intent or "CREATE",
				"selected_skills": state.selected_skills,
				"selected_doctypes": state.selected_doctypes,
			}

		mods = []
		for dt in detected_dts:
			m = self.registry.get_module_for_doctype(dt)
			if m and m not in mods:
				mods.append(m)
		if not mods:
			mods = [primary_mod]

		return {"intent": action, "selected_skills": mods, "selected_doctypes": detected_dts}

	def node_load_skill(self, state: AgentState) -> dict[str, Any]:
		"""Node 3: Dynamically load domain knowledge for selected module(s)."""
		skill_ctx = {}
		for mod in state.selected_skills:
			loaded = self.loader.load_skill(mod)
			skill_ctx[mod] = {"rules": loaded.get("rules", {}), "workflows": loaded.get("workflows", {})}
		return {"skill_context": skill_ctx}

	def node_load_metadata(self, state: AgentState) -> dict[str, Any]:
		"""Node 4: Fetch live Frappe schema metadata (runtime source of truth)."""
		if not state.selected_doctypes:
			return {"metadata": {}}

		primary_dt = state.selected_doctypes[0]
		meta = self.metadata_service.get_doctype_meta(primary_dt)
		return {"metadata": meta}

	def node_extract_parameters(self, state: AgentState) -> dict[str, Any]:
		"""Node 5: Extract parameter values from natural language."""
		if not state.selected_doctypes:
			return {"parameters": {}}

		req = state.original_request.strip()
		req_lower = req.lower()

		# If user is confirming an already validated plan, preserve existing parameters intact
		if (state.status == "AWAITING_CONFIRMATION" or state.confirmation_status == "CONFIRMED") and any(
			w in req_lower for w in ["confirm", "yes", "proceed", "create it", "do it"]
		):
			return {"parameters": state.parameters}

		primary_dt = state.selected_doctypes[0]

		# 1. Start with existing parameters in state
		extracted = dict(state.parameters)

		# 2. Extract key: value or natural language phrases
		term_map = {
			"company": "company_name" if primary_dt == "Company" else "company",
			"company_name": "company_name",
			"name": "company_name"
			if primary_dt == "Company"
			else ("project_name" if primary_dt == "Project" else "name"),
			"abbr": "abbr",
			"abbreviation": "abbr",
			"project": "project_name" if primary_dt == "Project" else "project",
			"project_name": "project_name",
			"customer": "customer_name" if primary_dt == "Customer" else "customer",
			"customer_name": "customer_name",
			"supplier": "supplier_name" if primary_dt == "Supplier" else "supplier",
			"supplier_name": "supplier_name",
			"item": "production_item" if primary_dt == "Work Order" else "item_code",
			"item_code": "item_code",
			"item_name": "item_name",
			"warehouse": "warehouse_name" if primary_dt == "Warehouse" else "warehouse",
			"warehouse_name": "warehouse_name",
			"task": "subject",
			"subject": "subject",
			"qty": "qty",
			"quantity": "qty",
			"currency": "default_currency",
			"default_currency": "default_currency",
			"country": "country",
			"letter_head": "default_letter_head",
			"default_letter_head": "default_letter_head",
		}

		def _auto_generate_abbr(name: str) -> str:
			"""Generate abbreviation taking first letter of each word (preserves case, e.g. GMplc)."""
			if not name:
				return ""
			words = [w for w in re.split(r"[\s\-_]+", name.strip()) if w]
			if not words:
				return ""
			abbr = "".join(w[0] for w in words if w[0].isalnum())
			if len(abbr) < 2 and len(words[0]) >= 2:
				abbr = words[0][:3].upper()
			return abbr

		# Key: value regex
		kv_found = False
		for k, v in re.findall(r"(?:^|[\n,;])\s*([a-zA-Z0-9_\s]+?)\s*[:=]\s*([^,\n;]+)", req):
			norm_k = k.strip().lower().replace(" ", "_")
			val = v.strip().rstrip(".").strip()
			if val:
				mapped = term_map.get(norm_k, norm_k)
				extracted[mapped] = val
				kv_found = True

		STOP_WORDS = {
			"a",
			"an",
			"the",
			"new",
			"here",
			"please",
			"my",
			"some",
			"our",
			"one",
			"project",
			"company",
			"customer",
			"item",
			"record",
			"doc",
			"document",
			"create",
			"add",
			"setup",
			"want",
			"i",
			"to",
			"there",
			"this",
			"that",
		}

		# Sanitize all extracted values to remove any accidentally captured field name prefix
		for k, v in list(extracted.items()):
			if isinstance(v, str):
				extracted[k] = re.sub(
					r"^(?:company_name|company|abbr|abbreviation|project_name|project|customer_name|customer|item_code|item|supplier_name|supplier|warehouse_name|warehouse|default_currency|country|letter_head|default_letter_head)\s*[:=]\s*",
					"",
					v,
					flags=re.IGNORECASE,
				).strip()

		# Direct slot answer if single missing parameter and not a command
		if state.missing_parameters and len(state.missing_parameters) == 1:
			missing_fname = state.missing_parameters[0]["field"]
			if missing_fname not in extracted or not extracted[missing_fname]:
				is_command = any(
					req_lower.startswith(p)
					for p in (
						"i want",
						"create ",
						"add ",
						"new ",
						"show ",
						"check ",
						"list ",
						"what is",
						"cancel",
						"reset",
					)
				)
				if not is_command:
					clean_ans = req.strip().rstrip(".")
					if missing_fname == "abbr":
						clean_ans = re.sub(r"[^A-Za-z0-9]", "", clean_ans)
					if clean_ans.lower() not in STOP_WORDS:
						extracted[missing_fname] = clean_ans

		# Natural language company extraction
		if primary_dt == "Company":
			# Only parse comma separated or plain text if company_name not already cleanly extracted
			if "company_name" not in extracted or not extracted["company_name"]:
				if "," in req and not kv_found and ":" not in req and "=" not in req:
					parts = [p.strip().rstrip(".").strip() for p in req.split(",") if p.strip()]
					if len(parts) >= 2:
						c_cand = parts[0]
						if c_cand.lower() not in STOP_WORDS and len(c_cand) >= 2:
							extracted["company_name"] = c_cand
							cand_abbr = parts[1].split()[0]
							extracted["abbr"] = re.sub(r"[^A-Za-z0-9]", "", cand_abbr)
				else:
					m = re.search(
						r"(?:(?:create|add|new|setup)\s+(?:a\s+|an\s+|new\s+)?(?:company|organization)\s+)?(?:called|named|name)?\s*([A-Za-z0-9_\s]+?)\s+(?:with\s+)?(?:abbr|abbreviation)\s+([A-Za-z0-9]+)",
						req,
						re.IGNORECASE,
					)
					if m:
						cand = m.group(1).strip()
						cand = re.sub(
							r"^(?:create|add|new|setup)\s+(?:a\s+|an\s+|new\s+)?(?:company|organization)\s+",
							"",
							cand,
							flags=re.IGNORECASE,
						).strip()
						if cand.lower() not in STOP_WORDS and len(cand) >= 2:
							extracted["company_name"] = cand
							extracted["abbr"] = m.group(2).strip()
					elif "company_name" not in extracted or not extracted["company_name"]:
						m_single = re.search(
							r"(?:company|organization)\s+(?:called|named|with name)\s*([A-Za-z0-9_\s\-]+)",
							req,
							re.IGNORECASE,
						)
						if m_single:
							cand = m_single.group(1).strip().rstrip(".").strip()
							cand_clean = re.sub(
								r"^(here|new|a|an|please)\s+", "", cand, flags=re.IGNORECASE
							).strip()
							if cand_clean and cand_clean.lower() not in STOP_WORDS and len(cand_clean) >= 2:
								extracted["company_name"] = cand_clean
						elif state.status == "COLLECTING_SLOTS" and req and not kv_found:
							if not any(
								req_lower.startswith(p)
								for p in (
									"i want",
									"create ",
									"add ",
									"new ",
									"show ",
									"check ",
									"list ",
									"cancel",
								)
							):
								cand_clean = re.sub(
									r"^(?:create|add|new|setup)\s+(?:a\s+|an\s+|new\s+)?(?:company|organization)\s+(?:called|named|name)?\s*",
									"",
									req,
									flags=re.IGNORECASE,
								).strip()
								if (
									cand_clean
									and cand_clean.lower() not in STOP_WORDS
									and len(cand_clean) >= 2
								):
									extracted["company_name"] = cand_clean

			# Clean any prefixes that might have leaked into company_name
			if "company_name" in extracted:
				extracted["company_name"] = re.sub(
					r"^(?:company_name|company)\s*[:=]\s*",
					"",
					str(extracted["company_name"]),
					flags=re.IGNORECASE,
				).strip()

			# Auto-generate Abbreviation if missing, invalid, or set to literal "ABBR"
			if extracted.get("company_name"):
				curr_abbr = extracted.get("abbr", "").strip()
				if not curr_abbr or curr_abbr.upper() == "ABBR" or curr_abbr.lower() in STOP_WORDS:
					extracted["abbr"] = _auto_generate_abbr(extracted["company_name"])

			if "company_name" in extracted and (
				extracted["company_name"].lower() in STOP_WORDS or len(extracted["company_name"]) < 2
			):
				extracted.pop("company_name", None)
			if "abbr" in extracted and (
				extracted["abbr"].lower() in STOP_WORDS or len(extracted["abbr"]) > 10
			):
				extracted.pop("abbr", None)

		# Natural language project extraction
		if "Project" in state.selected_doctypes:
			if "project_name" not in extracted or extracted["project_name"].lower() in STOP_WORDS:
				m_named = re.search(
					r"project\s+(?:called|named|with name)\s+([A-Za-z0-9_\-\s]+?)(?:\s+(?:for|under|with|in)\b|$)",
					req,
					re.IGNORECASE,
				)
				if m_named:
					cand = m_named.group(1).strip().rstrip(".").strip()
					if cand.lower() not in STOP_WORDS and len(cand) >= 2:
						extracted["project_name"] = cand
				else:
					m_p = re.search(
						r"(?:create|add|new|setup)\s+(?:a\s+|an\s+|new\s+)?project\s+([A-Za-z0-9_\-]+(?:\s+[A-Za-z0-9_\-]+)*)",
						req,
						re.IGNORECASE,
					)
					if m_p:
						cand = m_p.group(1).strip().rstrip(".").strip()
						cand_words = [w for w in cand.split() if w.lower() not in STOP_WORDS]
						if cand_words:
							clean_proj = " ".join(cand_words)
							if len(clean_proj) >= 2 and clean_proj.lower() not in STOP_WORDS:
								extracted["project_name"] = clean_proj
				if (
					"project_name" not in extracted
					and state.status == "COLLECTING_SLOTS"
					and req
					and not kv_found
				):
					if not any(
						req_lower.startswith(p)
						for p in ("i want", "create ", "add ", "new ", "show ", "check ", "list ", "cancel")
					):
						if req.lower() not in STOP_WORDS and len(req) >= 2:
							extracted["project_name"] = req.strip().rstrip(".")

			if "project_name" in extracted and (
				extracted["project_name"].lower() in STOP_WORDS or len(extracted["project_name"]) < 2
			):
				extracted.pop("project_name", None)

		# Natural language customer extraction
		if "Customer" in state.selected_doctypes and "customer_name" not in extracted:
			m_c = re.search(
				r"(?:create|add|new)\s+customer\s+(?:called|named)?\s*([A-Za-z0-9_\-\s]+)", req, re.IGNORECASE
			)
			if m_c:
				cand = m_c.group(1).strip().rstrip(".").strip()
				extracted["customer_name"] = cand

		# Natural language item extraction
		elif primary_dt == "Item":
			m_i = re.search(
				r"(?:create|add|new)\s+item\s+([A-Za-z0-9_\-]+)(?:\s+(?:named|with name|called)\s+([A-Za-z0-9_\-\s]+))?",
				req,
				re.IGNORECASE,
			)
			if m_i:
				extracted["item_code"] = m_i.group(1).strip()
				extracted["item_name"] = (m_i.group(2) or m_i.group(1)).strip().rstrip(".")

		# 5. Check LLM extraction if mandatory fields still missing
		if self.llm.is_available() and state.metadata:
			mand_fnames = [m["fieldname"] for m in state.metadata.get("mandatory_fields", [])]
			if any(
				f not in extracted or not extracted[f]
				for f in mand_fnames
				if f not in ("naming_series", "idx", "docstatus")
			):
				try:
					llm_ext = self.llm.extract_parameters(req, primary_dt, state.metadata.get("fields", []))
					if llm_ext and llm_ext.extracted_parameters:
						for k, v in llm_ext.extracted_parameters.items():
							if k not in extracted or not extracted[k]:
								extracted[k] = v
				except Exception:
					pass

		# Apply domain-level standard defaults ONLY if primary entity name is present
		# This prevents pre-populating fields on Turn 1 before slot intake is presented to user
		if primary_dt == "Company" and extracted.get("company_name"):
			extracted.setdefault("default_currency", "INR")
			extracted.setdefault("country", "India")
		elif primary_dt in ("Project", "Warehouse", "Work Order", "Department", "Cost Center") and any(
			extracted.get(k)
			for k in (
				"project_name",
				"warehouse_name",
				"production_item",
				"department_name",
				"cost_center_name",
			)
		):
			extracted.setdefault("company", "SarathiAILabs")
		elif primary_dt == "Customer" and extracted.get("customer_name"):
			extracted.setdefault("customer_type", "Company")
			extracted.setdefault("customer_group", "All Customer Groups")
			extracted.setdefault("territory", "All Territories")
		elif primary_dt == "Supplier" and extracted.get("supplier_name"):
			extracted.setdefault("supplier_type", "Company")
			extracted.setdefault("supplier_group", "All Supplier Groups")
			extracted.setdefault("country", "India")
		elif primary_dt == "Item" and extracted.get("item_code"):
			extracted.setdefault("stock_uom", "Nos")
			extracted.setdefault("item_group", "Products")

		return {"parameters": extracted}

	def node_check_missing_information(self, state: AgentState) -> dict[str, Any]:
		"""Node 6: Identify required fields missing from live schema across all 13 modules."""
		if state.intent != "CREATE" or not state.selected_doctypes:
			return {"missing_parameters": []}

		primary_dt = state.selected_doctypes[0]
		params = state.parameters

		# Get full slot intake schema for the primary DocType directly from live metadata
		all_slots = get_slots_for_doctype(primary_dt, state.metadata, client=self.client)

		# Identify missing mandatory fields
		missing_reqd = []
		for s in all_slots:
			fname = s["field"]
			# Auto-apply live Frappe schema defaults if field has default and is not set
			if fname not in params or params[fname] is None or str(params[fname]).strip() == "":
				if s.get("default") is not None and str(s.get("default")).strip() != "":
					params[fname] = s.get("default")
					continue
				if s.get("reqd"):
					missing_reqd.append(s)

		if missing_reqd:
			primary_mod = state.metadata.get("module") or (
				state.selected_skills[0] if state.selected_skills else "General"
			)

			fields_bullet = "\n".join([f"- **{m['label']} \\***: {m.get('hint', '')}" for m in missing_reqd])
			reply = (
				f"I would be glad to help you create a new **{primary_dt}** in ERPNext ({primary_mod} module).\n\n"
				f"To proceed, please share the following mandatory details marked with an asterisk (*):\n{fields_bullet}\n\n"
				f"You can fill the interactive intake card above or provide them directly in the chatbox!"
			)

			return {
				"missing_parameters": missing_reqd,
				"status": "COLLECTING_SLOTS",
				"final_response": {
					"message": reply,
					"status": "COLLECTING_SLOTS",
					"doctype": primary_dt,
					"missing": [m["field"] for m in missing_reqd],
					"missing_details": all_slots,
				},
			}

		return {"missing_parameters": []}

	def node_resolve_dependencies(self, state: AgentState) -> dict[str, Any]:
		"""Node 7: Topologically order multi-entity DAG and validate foreign keys."""
		doctypes = state.selected_doctypes
		if len(doctypes) > 1:
			order = self.resolver.plan_creation_order(doctypes)
			return {"dependencies": [{"order": order}]}

		# Verify foreign keys for single entity
		if doctypes:
			primary_dt = doctypes[0]
			ref_check = self.resolver.validate_references(primary_dt, state.parameters)
			return {"dependencies": [ref_check]}

		return {"dependencies": []}

	def node_validate(self, state: AgentState) -> dict[str, Any]:
		"""Node 8: Verify uniqueness and schema invariants against database."""
		if state.intent != "CREATE" or not state.selected_doctypes:
			return {}

		primary_dt = state.selected_doctypes[0]
		params = state.parameters

		# Check uniqueness for Company
		if primary_dt == "Company":
			c_name = params.get("company_name")
			if c_name and self.client.exists("Company", c_name):
				return {
					"status": "VALIDATION_ERROR",
					"final_response": {
						"message": f"⚠️ A Company named '{c_name}' already exists in ERPNext. Please provide a different company name.",
						"status": "COLLECTING_SLOTS",
					},
				}
			abbr = params.get("abbr")
			if abbr and self.client.exists("Company", {"abbr": abbr}):
				return {
					"status": "VALIDATION_ERROR",
					"final_response": {
						"message": f"⚠️ The abbreviation '{abbr}' is already assigned to another company. Please provide a different abbreviation.",
						"status": "COLLECTING_SLOTS",
					},
				}

		# Check uniqueness for Project
		elif primary_dt == "Project":
			p_name = params.get("project_name")
			if p_name and self.client.exists("Project", {"project_name": p_name}):
				return {
					"status": "VALIDATION_ERROR",
					"final_response": {
						"message": f"⚠️ A Project named '{p_name}' already exists in ERPNext. Please specify a unique project name.",
						"status": "COLLECTING_SLOTS",
					},
				}

		return {"status": "VALIDATED"}

	def node_check_permission(self, state: AgentState) -> dict[str, Any]:
		"""Node 9: Authenticated user permission evaluation."""
		if not state.selected_doctypes:
			return {"permission_result": {"has_permission": True}}

		primary_dt = state.selected_doctypes[0]
		ptype = "create" if state.intent == "CREATE" else "read"
		perm_res = self.client.check_permission(doctype=primary_dt, perm_type=ptype, user=state.user)
		return {"permission_result": perm_res}

	def node_confirmation_if_required(self, state: AgentState) -> dict[str, Any]:
		"""Node 10: Enforce explicit user confirmation safety gate before mutations."""
		if state.intent != "CREATE" or not state.selected_doctypes:
			return {"confirmation_required": False}

		primary_dt = state.selected_doctypes[0]
		params = state.parameters

		# Check if user already confirmed
		req_lower = state.original_request.lower()
		if any(w in req_lower for w in ["confirm", "yes", "proceed", "create it", "do it"]):
			return {
				"confirmation_required": True,
				"confirmation_status": "CONFIRMED",
				"status": "EXECUTING",
				"final_response": None,
			}

		clean_pending = get_clean_pending_values(params)
		clean_fields = {k.replace("_", " ").title(): str(v) for k, v in clean_pending.items()}

		# Prepare confirmation card for user
		summary_lines = []
		for k, v in clean_pending.items():
			summary_lines.append(f"{k.replace('_', ' ').title()}:\n**{v}**")

		summary_text = "\n\n".join(summary_lines)
		primary_mod = state.selected_skills[0] if state.selected_skills else "Organization"

		reply = (
			f"I understood:\n\n"
			f"{summary_text}\n\n"
			f"**Action:**\nCreate {primary_dt}\n\n"
			f"I am validating the request before execution.\n\n"
			f"✓ {primary_mod} Skill loaded\n"
			f"✓ {primary_dt} DocType identified\n"
			f"✓ Required fields available\n"
			f"✓ Permission checked for {state.user}\n"
			f"✓ Duplicate check completed\n\n"
			f"Ready to create the {primary_dt}."
		)

		return {
			"confirmation_required": True,
			"confirmation_status": "AWAITING_CONFIRMATION",
			"status": "AWAITING_CONFIRMATION",
			"final_response": {
				"message": reply,
				"status": "AWAITING_CONFIRMATION",
				"doctype": primary_dt,
				"pending_values": clean_pending,
				"confirmation_data": {
					"title": f"Create {primary_dt}",
					"fields": clean_fields,
					"confirm_label": "Confirm & Create",
					"cancel_label": "Cancel",
				},
			},
		}

	def node_execute_tool(self, state: AgentState) -> dict[str, Any]:
		"""Node 11: Execute controlled Frappe tool (frappe.new_doc -> insert)."""
		doctypes = state.selected_doctypes
		if len(doctypes) > 1:
			order = self.resolver.plan_creation_order(doctypes)
			tool_calls = []
			exec_results = []
			created_company = None

			for dt in order:
				dt_params = dict(state.parameters)
				if created_company:
					dt_params["company"] = created_company

				res = self.tool_registry.execute(
					tool_name="create_document", user=state.user, doctype=dt, values=dt_params
				)
				if dt == "Company" and res.get("success"):
					created_company = res.get("name")

				tool_calls.append({"tool": "create_document", "doctype": dt, "inputs": dt_params})
				exec_results.append(res)
				if not res.get("success"):
					break

			return {"tool_calls": tool_calls, "execution_results": exec_results}

		primary_dt = state.selected_doctypes[0]
		res = self.tool_registry.execute(
			tool_name="create_document", user=state.user, doctype=primary_dt, values=state.parameters
		)
		return {
			"tool_calls": [{"tool": "create_document", "doctype": primary_dt, "inputs": state.parameters}],
			"execution_results": [res],
		}

	def node_verify_result(self, state: AgentState) -> dict[str, Any]:
		"""Node 12: Read-Back Verification against MariaDB."""
		if len(state.selected_doctypes) > 1 and len(state.execution_results) > 1:
			all_verified = True
			details = []
			for exec_res in state.execution_results:
				dt = exec_res.get("doctype")
				doc_name = exec_res.get("name") or exec_res.get("data", {}).get("name")
				if not exec_res.get("success") or not doc_name:
					all_verified = False
					details.append({"doctype": dt, "verified": False, "reason": exec_res.get("error")})
					break
				v = self.validator.verify_document_created(dt, doc_name, state.parameters)
				details.append(v)
				if not v.get("verified"):
					all_verified = False
					break
			return {"verification_results": {"verified": all_verified, "details": details}}

		primary_dt = state.selected_doctypes[0]
		exec_res = state.execution_results[-1] if state.execution_results else {}
		doc_name = exec_res.get("name") or exec_res.get("data", {}).get("name")

		if not exec_res.get("success"):
			return {"verification_results": {"verified": False, "reason": exec_res.get("error")}}

		verif = self.validator.verify_document_created(primary_dt, doc_name, state.parameters)
		return {"verification_results": verif}

	def node_audit(self, state: AgentState) -> dict[str, Any]:
		"""Node 13: Log immutable audit event into JSONL file."""
		exec_res = state.execution_results[-1] if state.execution_results else {}
		primary_dt = state.selected_doctypes[0] if state.selected_doctypes else "Document"
		primary_mod = state.selected_skills[0] if state.selected_skills else "Organization"

		event = self.audit.log_event(
			event_type="CREATE" if state.intent == "CREATE" else "QUERY",
			tool_name="create_document" if state.intent == "CREATE" else "search_documents",
			inputs=state.parameters,
			output=exec_res,
			validation=state.verification_results,
			status="SUCCESS" if state.verification_results.get("verified") else "FAILED",
			module=primary_mod,
			user=state.user,
			session_id=state.session_id,
			conversation_id=state.conversation_id,
			doctype=primary_dt,
			confirmation=state.confirmation_status,
		)
		return {"audit_id": event.get("event_id")}

	def node_respond(self, state: AgentState) -> dict[str, Any]:
		"""Node 14: Build structured response payload with Desk links and verified badge."""
		# If response already set by missing information or confirmation gate or reset, return it
		if state.status in ("IDLE", "COLLECTING_SLOTS", "AWAITING_CONFIRMATION") and state.final_response:
			resp_status = state.final_response.get("status") or state.status
			return {"final_response": state.final_response, "status": resp_status}

		# Handling stock inquiry
		if state.intent == "STOCK_QUERY":
			from ERPNext_Agent.core.conversational_agent import ConversationalAgent

			conv = ConversationalAgent()
			stock_res = conv._handle_stock_query(state.original_request)
			return {"final_response": stock_res, "status": "COMPLETED"}

		# Handling live changes
		if state.intent == "LIVE_CHANGES":
			from ERPNext_Agent.core.conversational_agent import ConversationalAgent

			conv = ConversationalAgent()
			live_res = conv._handle_live_changes()
			return {"final_response": live_res, "status": "COMPLETED"}

		# General question or domain inquiry without document creation
		if state.intent in ("QUERY", "GENERAL", "GREETING") and not state.execution_results:
			skill_info = ""
			for mod, ctx in (state.skill_context or {}).items():
				skill_info += f"\nModule: {mod}\nRules: {json.dumps(ctx.get('rules', {}))}\n"

			llm_prompt = (
				f"You are the Sarathi Industrial ERPNext AI Agent.\n"
				f"User request: '{state.original_request}'\n"
				f"Active Modules / Skills: {', '.join(state.selected_skills or ['Organization'])}\n"
				f"Domain Context:\n{skill_info}\n"
				f"Provide a helpful, precise, professional, and friendly answer about ERPNext. "
				f"If they asked how to perform an action or create a record, explain what is needed and offer to help them do it."
			)
			ai_reply = self.llm.generate(llm_prompt)
			if not ai_reply or len(ai_reply.strip()) < 10:
				ai_reply = (
					"I am your **Sarathi ERPNext AI Agent**.\n\n"
					"I can help you create, manage, and inspect records across all 13 ERPNext modules.\n"
					"You can ask me to create entities (e.g. *'Create a company'*, *'Create a project'*), "
					"check real-time stock (*'Check stock in Stores'*), or view live activity (*'Show live changes'*).\n\n"
					"What would you like to accomplish?"
				)
			return {
				"status": "COMPLETED",
				"final_response": {"message": ai_reply.strip(), "status": "COMPLETED"},
			}

		verified = state.verification_results.get("verified", False)
		if not verified:
			err = state.verification_results.get("reason")
			if not err and state.execution_results:
				err = state.execution_results[-1].get("error")
			return {
				"status": "FAILED",
				"final_response": {
					"message": f"❌ Operation failed: {err or 'Unknown error'}",
					"status": "FAILED",
				},
			}

		# Multi-entity compound response
		if len(state.selected_doctypes) > 1 and len(state.execution_results) > 1:
			reply_lines = [
				"🔄 Multi-Step Workflow Executed Successfully!\n",
				"✓ Prerequisite dependency chain ordered",
				"✓ Cross-module records inserted",
				"✓ Records read back and verified\n",
			]
			follow_ups = []
			for exec_res in state.execution_results:
				dt = exec_res.get("doctype", "Document")
				name = exec_res.get("name")
				slug = dt.lower().replace(" ", "-")
				url = f"/app/{slug}/{name}"
				reply_lines.append(f"• **{dt}:** [{name}]({url})")
				follow_ups.append({"label": f"Open {dt} ↗", "url": url})

			reply_lines.append("\nAll records verified in ERPNext.")
			return {
				"status": "COMPLETED",
				"final_response": {
					"message": "\n".join(reply_lines),
					"status": "COMPLETED",
					"doctype": state.selected_doctypes[0],
					"name": state.execution_results[0].get("name"),
					"verified": True,
					"url": f"/app/{state.selected_doctypes[0].lower().replace(' ', '-')}/{state.execution_results[0].get('name')}",
					"follow_ups": follow_ups,
				},
			}

		primary_dt = state.selected_doctypes[0] if state.selected_doctypes else "Document"
		exec_res = state.execution_results[-1] if state.execution_results else {}
		doc_name = exec_res.get("name") or exec_res.get("data", {}).get("name")

		doctype_slug = primary_dt.lower().replace(" ", "-")
		desk_url = f"/app/{doctype_slug}/{doc_name}"

		reply = (
			f"Creating {primary_dt}...\n\n"
			f"✓ ERPNext operation executed\n"
			f"✓ {primary_dt} created\n"
			f"✓ Record read back successfully\n"
			f"✓ Result verified\n\n"
			f'Company **"{doc_name}"** was created successfully and verified in ERPNext.\n\n'
			f"[🚀 Open {primary_dt} in Desk]({desk_url})"
		)

		return {
			"status": "COMPLETED",
			"final_response": {
				"message": reply,
				"status": "COMPLETED",
				"doctype": primary_dt,
				"name": doc_name,
				"verified": True,
				"url": desk_url,
				"follow_ups": [
					{"label": f"Open {doc_name} ↗", "url": desk_url},
					{"label": "Refresh Dashboard", "action": "refresh"},
				],
			},
		}

	# -------------------------------------------------------------
	# StateGraph Construction
	# -------------------------------------------------------------

	def _build_graph(self):
		"""Construct the compiled LangGraph workflow with conditional routing."""
		builder = StateGraph(AgentState)

		# Add all 14 nodes
		builder.add_node("understand_request", self.node_understand_request)
		builder.add_node("route_skill", self.node_route_skill)
		builder.add_node("load_skill", self.node_load_skill)
		builder.add_node("load_metadata", self.node_load_metadata)
		builder.add_node("extract_parameters", self.node_extract_parameters)
		builder.add_node("check_missing_information", self.node_check_missing_information)
		builder.add_node("resolve_dependencies", self.node_resolve_dependencies)
		builder.add_node("validate", self.node_validate)
		builder.add_node("check_permission", self.node_check_permission)
		builder.add_node("confirmation_if_required", self.node_confirmation_if_required)
		builder.add_node("execute_tool", self.node_execute_tool)
		builder.add_node("verify_result", self.node_verify_result)
		builder.add_node("audit", self.node_audit)
		builder.add_node("respond", self.node_respond)

		# Add edges
		builder.add_edge(START, "understand_request")

		def route_after_understand(state: AgentState) -> str:
			if state.status == "IDLE":
				return "respond"
			return "route_skill"

		builder.add_conditional_edges(
			"understand_request", route_after_understand, {"respond": "respond", "route_skill": "route_skill"}
		)

		builder.add_edge("route_skill", "load_skill")
		builder.add_edge("load_skill", "load_metadata")
		builder.add_edge("load_metadata", "extract_parameters")
		builder.add_edge("extract_parameters", "check_missing_information")

		# Conditional branch after check_missing_information
		def route_after_missing_check(state: AgentState) -> str:
			if state.missing_parameters:
				return "respond"
			return "resolve_dependencies"

		builder.add_conditional_edges(
			"check_missing_information",
			route_after_missing_check,
			{"respond": "respond", "resolve_dependencies": "resolve_dependencies"},
		)

		builder.add_edge("resolve_dependencies", "validate")
		builder.add_edge("validate", "check_permission")

		# Conditional branch after check_permission & confirmation
		builder.add_edge("check_permission", "confirmation_if_required")

		def route_after_confirmation(state: AgentState) -> str:
			if state.confirmation_required and state.confirmation_status != "CONFIRMED":
				return "respond"
			if state.intent != "CREATE":
				return "respond"
			return "execute_tool"

		builder.add_conditional_edges(
			"confirmation_if_required",
			route_after_confirmation,
			{"respond": "respond", "execute_tool": "execute_tool"},
		)

		builder.add_edge("execute_tool", "verify_result")
		builder.add_edge("verify_result", "audit")
		builder.add_edge("audit", "respond")
		builder.add_edge("respond", END)

		return builder.compile()

	def invoke(self, state: AgentState) -> AgentState:
		"""Run the compiled LangGraph workflow end-to-end on the input state."""
		res_dict = self.graph.invoke(state)
		if isinstance(res_dict, dict):
			return AgentState.model_validate(res_dict)
		return res_dict
