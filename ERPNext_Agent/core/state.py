"""Pydantic Agent State for LangGraph Orchestration and Multi-Turn Conversation.

Tracks complete contextual state across all 14 pipeline nodes:
Intent -> Routing -> Skill Loading -> Live Metadata -> Extraction ->
Validation -> Dependencies -> Permission -> Confirmation -> Execution ->
Verification -> Audit -> Response.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentState(BaseModel):
	"""Strong Pydantic state model for LangGraph Agent orchestration."""

	# 1. Identity & Session
	session_id: str = Field(default="default_session", description="Unique session ID")
	conversation_id: str | None = Field(default=None, description="Client conversation tracking ID")
	user: str = Field(default="Administrator", description="Authenticated Frappe user (frappe.session.user)")

	# 2. Input & Request Understanding
	original_request: str = Field(default="", description="Raw natural language prompt from user")
	intent: str = Field(
		default="QUERY", description="Classified action: CREATE, UPDATE, DELETE, SUBMIT, etc."
	)

	# 3. Domain Skills & Entity Mapping
	selected_skills: list[str] = Field(
		default_factory=list, description="Target modules (e.g. ['Organization', 'Projects'])"
	)
	selected_doctypes: list[str] = Field(
		default_factory=list, description="Target DocTypes (e.g. ['Company', 'Project'])"
	)
	skill_context: dict[str, Any] = Field(
		default_factory=dict, description="Domain rules and knowledge loaded from skills"
	)

	# 4. Live ERPNext Metadata
	metadata: dict[str, Any] = Field(
		default_factory=dict, description="Live Frappe schema from frappe.get_meta()"
	)

	# 5. Parameters & Discovery
	parameters: dict[str, Any] = Field(
		default_factory=dict, description="Extracted parameters and slot values"
	)
	missing_parameters: list[dict[str, Any]] = Field(
		default_factory=list, description="Mandatory fields still required"
	)

	# 6. Cross-Module Dependencies & Planning
	dependencies: list[dict[str, Any]] = Field(
		default_factory=list, description="Prerequisite entities and DAG order"
	)
	execution_plan: list[dict[str, Any]] = Field(
		default_factory=list, description="Scheduled sequence of tool actions"
	)

	# 7. Safety, Permissions & Confirmation
	permission_result: dict[str, Any] = Field(
		default_factory=dict, description="Permission evaluation for user"
	)
	confirmation_required: bool = Field(
		default=False, description="Whether safety gate requires confirmation"
	)
	confirmation_status: str = Field(default="PENDING", description="PENDING, CONFIRMED, CANCELLED")

	# 8. Execution, Tools & Verification
	tool_calls: list[dict[str, Any]] = Field(
		default_factory=list, description="Tools invoked during pipeline"
	)
	execution_results: list[dict[str, Any]] = Field(
		default_factory=list, description="Outputs from tool executions"
	)
	verification_results: dict[str, Any] = Field(
		default_factory=dict, description="ReadBackValidator comparison proof"
	)

	# 9. Audit & Lifecycle Status
	audit_id: str | None = Field(default=None, description="Unique ID of immutable audit event")
	status: str = Field(
		default="IDLE",
		description="Lifecycle state: IDLE, COLLECTING_SLOTS, AWAITING_CONFIRMATION, COMPLETED, FAILED",
	)
	final_response: dict[str, Any] | None = Field(
		default=None, description="Formatted response payload sent to Chatbox UI"
	)

	# 10. Multi-step Queue
	pending_queue: list[dict[str, Any]] = Field(
		default_factory=list, description="Queued steps for compound multi-entity workflows"
	)
	completed_steps: list[dict[str, Any]] = Field(
		default_factory=list, description="Completed pipeline step summaries"
	)

	def to_dict(self) -> dict[str, Any]:
		"""Convert state to dictionary for Redis cache serialization."""
		return self.model_dump()

	@classmethod
	def from_dict(cls, data: dict[str, Any]) -> "AgentState":
		"""Reconstruct state from Redis dictionary."""
		return cls.model_validate(data)

	def reset(self):
		"""Reset contextual fields back to IDLE state."""
		self.original_request = ""
		self.intent = "QUERY"
		self.selected_skills = []
		self.selected_doctypes = []
		self.skill_context = {}
		self.metadata = {}
		self.parameters = {}
		self.missing_parameters = []
		self.dependencies = []
		self.execution_plan = []
		self.permission_result = {}
		self.confirmation_required = False
		self.confirmation_status = "PENDING"
		self.tool_calls = []
		self.execution_results = []
		self.verification_results = {}
		self.audit_id = None
		self.status = "IDLE"
		self.final_response = {}
		self.pending_queue = []
		self.completed_steps = []
