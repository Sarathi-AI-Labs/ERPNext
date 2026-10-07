"""Master ERPNext AI Agent Coordinator.

End-to-end autonomous controller orchestrating Intent Routing, Dynamic Skill Loading,
Cross-Module Dependency Resolution, Tool Execution, Read-Back Validation, and Audit Logging.
"""

import time
from typing import Any, Dict, List

from ERPNext_Agent.core.audit import AuditLogger
from ERPNext_Agent.core.loader import SkillLoader
from ERPNext_Agent.core.planner import ExecutionPlan, ExecutionPlanner
from ERPNext_Agent.core.resolver import DependencyResolver
from ERPNext_Agent.core.router import SkillRouter
from ERPNext_Agent.core.validator import ReadBackValidator
from ERPNext_Agent.tools.client import FrappeClient
from ERPNext_Agent.tools.document_tools import (
	CreateDocumentTool,
	DeleteDocumentTool,
	GetDocumentTool,
	UpdateDocumentTool,
)
from ERPNext_Agent.tools.meta_tools import (
	CheckPermissionTool,
	GetDocMetaTool,
)
from ERPNext_Agent.tools.query_tools import (
	GetCountTool,
	GetValueTool,
	SearchDocumentsTool,
)
from ERPNext_Agent.tools.report_tools import (
	RunReportTool,
)
from ERPNext_Agent.tools.workflow_tools import (
	AmendDocumentTool,
	CancelDocumentTool,
	SubmitDocumentTool,
)


class MasterERPNextAgent:
	"""Production-grade coordinator for Frappe / ERPNext agentic workflows."""

	def __init__(self, container_name: str = "frappe_docker_main-backend-1", site_name: str = "frontend"):
		self.client = FrappeClient(container_name=container_name, site_name=site_name)
		self.router = SkillRouter()
		self.loader = SkillLoader()
		self.resolver = DependencyResolver(self.client)
		self.validator = ReadBackValidator(self.client)
		self.audit = AuditLogger()
		self.planner = ExecutionPlanner()

		# Register tools
		self.tools = {
			"create_document": CreateDocumentTool(self.client),
			"get_document": GetDocumentTool(self.client),
			"update_document": UpdateDocumentTool(self.client),
			"delete_document": DeleteDocumentTool(self.client),
			"submit_document": SubmitDocumentTool(self.client),
			"cancel_document": CancelDocumentTool(self.client),
			"amend_document": AmendDocumentTool(self.client),
			"search_documents": SearchDocumentsTool(self.client),
			"get_value": GetValueTool(self.client),
			"get_count": GetCountTool(self.client),
			"get_doc_meta": GetDocMetaTool(self.client),
			"check_permission": CheckPermissionTool(self.client),
			"run_report": RunReportTool(self.client),
		}

	def execute_plan(self, plan: ExecutionPlan) -> dict[str, Any]:
		"""Execute a multi-step plan with validation and audit trail."""
		step_outputs: dict[str, Any] = {}
		execution_results: list[dict[str, Any]] = []

		for step in plan.steps:
			t0 = time.time()
			tool = self.tools.get(step.tool_name)
			if not tool:
				err = f"Tool '{step.tool_name}' not found."
				self.audit.log_event(
					"EXECUTION_ERROR",
					step.tool_name,
					step.parameters,
					None,
					None,
					0.0,
					"FAILED",
					err,
					plan.module,
				)
				return {"success": False, "error": err, "completed_steps": execution_results}

			# Substitute references from prior steps if any (e.g. {{step_1.name}})
			resolved_params = {}
			for k, v in step.parameters.items():
				if isinstance(v, str) and v.startswith("{{") and v.endswith("}}"):
					ref_key = v[2:-2].strip()
					parts = ref_key.split(".")
					if len(parts) == 2 and parts[0] in step_outputs:
						resolved_params[k] = step_outputs[parts[0]].get(parts[1])
					else:
						resolved_params[k] = v
				else:
					resolved_params[k] = v

			# Execute tool
			try:
				res = tool.execute(**resolved_params)
			except Exception as e:
				res = {"success": False, "error": str(e)}

			duration_ms = (time.time() - t0) * 1000

			# Post-validation check
			val_result = None
			if res.get("success") and step.expected_validation:
				doc_name = res.get("name") or resolved_params.get("name")
				if "docstatus" in step.expected_validation and doc_name:
					val_result = self.validator.verify_document_status(
						step.doctype, doc_name, step.expected_validation["docstatus"]
					)
				else:
					val_result = {"verified": True}

			step_status = (
				"SUCCESS"
				if res.get("success") and (val_result is None or val_result.get("verified", True))
				else "FAILED"
			)

			self.audit.log_event(
				event_type=step.tool_name.upper(),
				tool_name=step.tool_name,
				inputs=resolved_params,
				output=res,
				validation=val_result,
				duration_ms=duration_ms,
				status=step_status,
				error=res.get("error")
				or (val_result.get("reason") if val_result and not val_result.get("verified") else None),
				module=plan.module,
			)

			step_record = {
				"step_id": step.step_id,
				"tool_name": step.tool_name,
				"parameters": resolved_params,
				"result": res,
				"validation": val_result,
				"status": step_status,
			}
			execution_results.append(step_record)
			step_outputs[f"step_{step.step_id}"] = res

			if step_status == "FAILED" and step.critical:
				return {
					"success": False,
					"error": f"Step {step.step_id} ({step.description}) failed: {res.get('error') or (val_result.get('reason') if val_result else 'Unknown error')}",
					"plan_id": plan.plan_id,
					"completed_steps": execution_results,
				}

		return {
			"success": True,
			"plan_id": plan.plan_id,
			"goal": plan.goal,
			"steps_executed": len(execution_results),
			"completed_steps": execution_results,
			"final_data": execution_results[-1]["result"] if execution_results else None,
		}

	def handle_request(self, user_prompt: str) -> dict[str, Any]:
		"""High-level entrypoint: Route prompt, load skills, build plan, execute & return."""
		route_info = self.router.route(user_prompt)
		module = route_info["primary_module"]

		# Load skill for instructions & domain rules
		skill = self.loader.load_skill(module)

		# For simple queries, build and run directly
		if route_info["action"] == "QUERY" and route_info["detected_doctypes"]:
			target_dt = route_info["detected_doctypes"][0]
			plan = self.planner.create_single_query_plan(doctype=target_dt, filters={})
			exec_res = self.execute_plan(plan)
			return {
				"route": route_info,
				"execution": exec_res,
				"audit_summary": self.audit.get_session_summary(),
			}

		return {
			"route": route_info,
			"skill_instructions": skill.get("instructions", "")[:500] + "...",
			"message": f"Routed to module '{module}' with action '{route_info['action']}'. Ready for plan execution.",
		}
