"""Sarathi Industrial AI Agent Backend API Bridge.

Integrates the unified Master ERPNext Agent and Conversational State Machine
into Frappe's whitelisted REST endpoints for the Sarathi Control Tower dashboard.
Supports full multi-turn conversational intake, permission gating, confirmation cards,
controlled Frappe tools, read-back verification, and real-time dashboard synchronization.
"""

import json

import frappe

from ERPNext_Agent.core.state import AgentState
from ERPNext_Agent.core.workflow import SarathiAgentGraph
from ERPNext_Agent.tools.client import FrappeClient


def _get_agent_state(session_id: str, user: str) -> AgentState:
	"""Restore AgentState from Frappe Redis cache or initialize new state."""
	cached = frappe.cache.hget("sarathi_agent_graph_state", session_id)
	if cached:
		try:
			if isinstance(cached, str):
				data = json.loads(cached)
			else:
				data = cached
			return AgentState.from_dict(data)
		except Exception as e:
			frappe.log_error(f"Error restoring AgentState: {e}", "SarathiAgentGraph")
	return AgentState(session_id=session_id, user=user)


def _persist_agent_state(session_id: str, state: AgentState):
	"""Persist current AgentState to Frappe Redis cache."""
	try:
		frappe.cache.hset("sarathi_agent_graph_state", session_id, state.to_dict())
	except Exception as e:
		frappe.log_error(f"Error persisting AgentState: {e}", "SarathiAgentGraph")


@frappe.whitelist(methods=["POST"])
def send_message(message, session_id=None, company=None, customer=None, project=None):
	"""Conversational endpoint for the Sarathi Dashboard chatbot."""
	user = frappe.session.user
	sid = session_id or user or "default_user"

	state = _get_agent_state(sid, user)
	state.original_request = message
	state.user = user

	# Apply ambient dashboard context if not already set (only if not creating a Company!)
	msg_lower = (message or "").lower()
	is_creating_company = (
		"company" in msg_lower and any(w in msg_lower for w in ["create", "new", "add", "setup", "want"])
	) or (state.selected_doctypes and state.selected_doctypes[0] == "Company")

	if company and "company" not in state.parameters and not is_creating_company:
		state.parameters["company"] = company
	if customer and "customer" not in state.parameters:
		state.parameters["customer"] = customer
	if project and "project" not in state.parameters:
		state.parameters["project"] = project

	# Execute LangGraph State Machine
	graph = SarathiAgentGraph(client=FrappeClient())
	res_state = graph.invoke(state)

	# Persist multi-turn conversation state
	_persist_agent_state(sid, res_state)

	response = res_state.final_response or {
		"message": "Instruction processed.",
		"status": res_state.status,
		"verified": res_state.verification_results.get("verified", False),
	}

	return response


@frappe.whitelist(methods=["GET"])
def get_suggestions(company=None, customer=None, project=None):
	"""Returns dynamic contextual prompt chips for the Sarathi dashboard."""
	chips = [
		{"label": "🏢 Create Company", "query": "I want to create a new company"},
		{"label": "🚀 Create Project", "query": "I want to create a project"},
		{"label": "⚡ Live Changes", "query": "Show live changes"},
		{"label": "📦 Check Stock", "query": "Check stock in Stores"},
		{"label": "💼 New Account Setup", "query": "New account setup"},
		{"label": "👥 Add Customer", "query": "Create a new customer"},
	]
	if project:
		chips.insert(0, {"label": f"📊 Status of {project}", "query": f"Check status of {project}"})
	elif customer:
		chips.insert(0, {"label": f"📂 Projects for {customer}", "query": f"Show projects for {customer}"})

	return {"suggestions": chips}
