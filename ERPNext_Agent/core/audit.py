"""Structured Audit Logger for ERPNext AI Agent.

Tracks all tool invocations, validation outcomes, errors, and database modifications
into persistent structured JSONL audit logs.
"""

import json
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class AuditLogger:
	"""Manages immutable audit trails for all Agent and Skill operations."""

	def __init__(self, log_dir: str | None = None):
		if log_dir is None:
			# Default to ERPNext_Agent/logs
			base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
			log_dir = os.path.join(base_dir, "logs")
		self.log_dir = log_dir
		os.makedirs(self.log_dir, exist_ok=True)
		self.log_file = os.path.join(self.log_dir, "agent_audit.jsonl")
		self.session_events: list[dict[str, Any]] = []

	def _sanitize(self, data: Any) -> Any:
		"""Mask sensitive keys like passwords or api secrets."""
		if isinstance(data, dict):
			sanitized = {}
			for k, v in data.items():
				if any(secret_word in k.lower() for secret_word in ["password", "secret", "token", "key"]):
					sanitized[k] = "********"
				else:
					sanitized[k] = self._sanitize(v)
			return sanitized
		elif isinstance(data, list):
			return [self._sanitize(item) for item in data]
		return data

	def log_event(
		self,
		event_type: str,
		tool_name: str,
		inputs: dict[str, Any],
		output: Any,
		validation: dict[str, Any] | None = None,
		duration_ms: float = 0.0,
		status: str = "SUCCESS",
		error: str | None = None,
		module: str | None = None,
		user: str | None = None,
		session_id: str | None = None,
		conversation_id: str | None = None,
		doctype: str | None = None,
		confirmation: str | None = None,
	) -> dict[str, Any]:
		"""Record an execution step into the audit trail."""
		event_id = f"audit_{int(time.time() * 1000)}"
		event = {
			"event_id": event_id,
			"timestamp": datetime.now(timezone.utc).isoformat(),
			"user": user or "Administrator",
			"session_id": session_id,
			"conversation_id": conversation_id,
			"module": module or "General",
			"doctype": doctype,
			"event_type": event_type,
			"tool_name": tool_name,
			"status": status,
			"confirmation": confirmation,
			"inputs": self._sanitize(inputs),
			"output": self._sanitize(output),
			"validation": validation,
			"duration_ms": round(duration_ms, 2),
			"error": error,
		}

		self.session_events.append(event)

		try:
			with open(self.log_file, "a", encoding="utf-8") as f:
				f.write(json.dumps(event, default=str) + "\n")
		except Exception as e:
			print(f"[AuditLogger Error] Could not write audit log: {e}")

		return event

	def get_session_summary(self) -> dict[str, Any]:
		"""Summarize all operations executed in current session."""
		total = len(self.session_events)
		successful = sum(1 for e in self.session_events if e.get("status") == "SUCCESS")
		failed = sum(1 for e in self.session_events if e.get("status") != "SUCCESS")
		mutations = [
			e
			for e in self.session_events
			if e.get("event_type") in ("CREATE", "UPDATE", "SUBMIT", "CANCEL", "DELETE")
		]

		return {
			"total_events": total,
			"successful_events": successful,
			"failed_events": failed,
			"total_mutations": len(mutations),
			"mutations": [
				{"tool": m["tool_name"], "inputs": m["inputs"], "status": m["status"]} for m in mutations
			],
		}
