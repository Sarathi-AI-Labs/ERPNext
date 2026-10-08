"""Multi-step Execution Planner for ERPNext AI Agent.

Deconstructs complex high-level goals into an ordered sequence of atomic tool
operations, dependency checks, and post-validation assertions.
"""

from typing import Any, Dict, List, Optional


class ExecutionStep:
	"""Represents a discrete atomic tool operation in an execution plan."""

	def __init__(
		self,
		step_id: int,
		tool_name: str,
		description: str,
		doctype: str,
		parameters: dict[str, Any],
		preconditions: list[str] | None = None,
		expected_validation: dict[str, Any] | None = None,
		critical: bool = True,
	):
		self.step_id = step_id
		self.tool_name = tool_name
		self.description = description
		self.doctype = doctype
		self.parameters = parameters
		self.preconditions = preconditions or []
		self.expected_validation = expected_validation or {}
		self.critical = critical

	def to_dict(self) -> dict[str, Any]:
		return {
			"step_id": self.step_id,
			"tool_name": self.tool_name,
			"description": self.description,
			"doctype": self.doctype,
			"parameters": self.parameters,
			"preconditions": self.preconditions,
			"expected_validation": self.expected_validation,
			"critical": self.critical,
		}


class ExecutionPlan:
	"""Contains an ordered list of steps and metadata."""

	def __init__(self, plan_id: str, goal: str, module: str):
		self.plan_id = plan_id
		self.goal = goal
		self.module = module
		self.steps: list[ExecutionStep] = []

	def add_step(self, step: ExecutionStep) -> None:
		self.steps.append(step)

	def to_dict(self) -> dict[str, Any]:
		return {
			"plan_id": self.plan_id,
			"goal": self.goal,
			"module": self.module,
			"total_steps": len(self.steps),
			"steps": [s.to_dict() for s in self.steps],
		}


class ExecutionPlanner:
	"""Constructs deterministic execution plans from routed user intents."""

	def create_single_query_plan(
		self, doctype: str, filters: dict[str, Any], fields: list[str] | None = None
	) -> ExecutionPlan:
		plan = ExecutionPlan(plan_id="query_single", goal=f"Query {doctype}", module=doctype)
		step = ExecutionStep(
			step_id=1,
			tool_name="search_documents",
			description=f"Search {doctype} matching filters",
			doctype=doctype,
			parameters={"doctype": doctype, "filters": filters, "fields": fields or ["name"]},
		)
		plan.add_step(step)
		return plan

	def create_mutation_plan(
		self, doctype: str, values: dict[str, Any], auto_submit: bool = False
	) -> ExecutionPlan:
		plan = ExecutionPlan(plan_id=f"create_{doctype.lower()}", goal=f"Create {doctype}", module=doctype)

		# Step 1: Pre-check existence / validation
		# Step 2: Create doc
		step_create = ExecutionStep(
			step_id=1,
			tool_name="create_document",
			description=f"Create new {doctype} document",
			doctype=doctype,
			parameters={"doctype": doctype, "values": values},
			expected_validation={"docstatus": 0},
		)
		plan.add_step(step_create)

		# Step 3: Optional auto-submit
		if auto_submit:
			step_submit = ExecutionStep(
				step_id=2,
				tool_name="submit_document",
				description=f"Submit created {doctype} document",
				doctype=doctype,
				parameters={"doctype": doctype, "name": "{{step_1.name}}"},
				expected_validation={"docstatus": 1},
			)
			plan.add_step(step_submit)

		return plan
