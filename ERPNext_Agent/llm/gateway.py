"""Unified LLM Gateway for ERPNext AI Agent.

Decouples the Agent state machine and tools from specific LLM providers (Ollama, etc.).
Provides automatic fallback, latency tracking, structured Pydantic extraction, and
guaranteed fail-safe behavior when the LLM is offline or unavailable.
"""

import time
from typing import Any, Dict, List, Optional

from ERPNext_Agent.llm.base import BaseLLMProvider
from ERPNext_Agent.llm.ollama import OllamaProvider
from ERPNext_Agent.llm.schemas import (
	LLMHealthStatus,
	LLMIntentClassification,
	LLMParameterExtraction,
)


class LLMGateway:
	"""Central gateway for all AI / LLM interactions across the ERPNext Agent."""

	def __init__(self, provider: BaseLLMProvider | None = None):
		self.provider = provider or OllamaProvider()

	def set_provider(self, provider: BaseLLMProvider):
		"""Swap or configure LLM provider at runtime."""
		self.provider = provider

	def is_available(self) -> bool:
		"""Check if active LLM backend is available."""
		return self.provider.is_available()

	def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
		"""Forward text generation to active LLM provider."""
		if not self.is_available():
			return ""
		return self.provider.generate(prompt, system_prompt=system_prompt, **kwargs)

	def health_check(self) -> LLMHealthStatus:
		"""Perform full health check with latency measurement."""
		t0 = time.time()
		avail = self.provider.is_available()
		lat = (time.time() - t0) * 1000.0

		base_url = getattr(self.provider, "base_url", "local")
		model = getattr(self.provider, "model", "default")
		provider_name = type(self.provider).__name__

		return LLMHealthStatus(
			provider=provider_name,
			available=avail,
			base_url=base_url,
			model=model,
			latency_ms=round(lat, 2),
			error=None if avail else "LLM service unreachable",
		)

	def classify_intent(self, user_message: str) -> LLMIntentClassification | None:
		"""Use LLM to classify user intent across 13 ERPNext modules into structured schema."""
		if not self.is_available():
			return None

		system_prompt = (
			"You are an enterprise ERPNext intent classification engine. "
			"Your task is to analyze user requests and map them accurately to ERPNext modules and DocTypes.\n"
			"Modules: Organization, Projects, Stock, Manufacturing, Selling, Buying, Accounting, Quality, Assets, Subcontracting, ERPNext Settings, Framework, Users and System.\n"
			"Actions: CREATE, UPDATE, DELETE, SUBMIT, CANCEL, AMEND, QUERY, REPORT."
		)

		prompt = (
			f"Classify the following ERPNext user instruction:\n\n"
			f'User Instruction: "{user_message}"\n\n'
			f"Determine the action, primary module, target DocType, and any secondary DocTypes."
		)

		return self.provider.generate_structured(
			prompt=prompt, schema=LLMIntentClassification, system_prompt=system_prompt
		)

	def extract_parameters(
		self, user_message: str, doctype: str, fields_schema: list[dict[str, Any]] | None = None
	) -> LLMParameterExtraction | None:
		"""Extract field values from natural language for a specific DocType."""
		if not self.is_available():
			return None

		schema_context = ""
		if fields_schema:
			schema_context = "Available DocType fields and their types:\n"
			for f in fields_schema[:25]:  # limit context to top fields
				req = " (Mandatory)" if f.get("reqd") else ""
				schema_context += f"- {f.get('fieldname')}: {f.get('label')} [{f.get('fieldtype')}]{req}\n"

		system_prompt = (
			f"You are a structured parameter extraction assistant for ERPNext DocType '{doctype}'.\n"
			f"{schema_context}\n"
			"Extract entity field values accurately from the user message into a key-value dictionary."
		)

		prompt = f"Extract parameters for DocType '{doctype}' from this instruction:\n\n" f'"{user_message}"'

		return self.provider.generate_structured(
			prompt=prompt, schema=LLMParameterExtraction, system_prompt=system_prompt
		)
