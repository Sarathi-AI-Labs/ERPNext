"""Ollama LLM Provider implementation for ERPNext AI Agent."""

import json
import os
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel

from ERPNext_Agent.llm.base import BaseLLMProvider


class OllamaProvider(BaseLLMProvider):
	"""Integrates local Ollama models with fail-safe error handling and JSON structured outputs."""

	def __init__(self, base_url: str | None = None, model: str | None = None):
		# Auto-detect default endpoint based on container environment
		if not base_url:
			env_url = os.environ.get("OLLAMA_BASE_URL")
			if env_url:
				self.base_url = env_url.rstrip("/")
			elif os.path.exists("/.dockerenv") or os.environ.get("FRAPPE_SITE"):
				self.base_url = "http://host.docker.internal:11434"
			else:
				self.base_url = "http://localhost:11434"
		else:
			self.base_url = base_url.rstrip("/")

		self.model = model or os.environ.get("OLLAMA_MODEL", "qwen2.5:1.5b")
		self.timeout = int(os.environ.get("OLLAMA_TIMEOUT", 15))

	def is_available(self) -> bool:
		"""Ping Ollama API to verify availability."""
		try:
			r = requests.get(f"{self.base_url}/api/tags", timeout=2)
			return r.status_code == 200
		except Exception:
			return False

	def list_models(self) -> list[str]:
		"""Fetch list of pulled models from Ollama."""
		try:
			r = requests.get(f"{self.base_url}/api/tags", timeout=3)
			if r.status_code == 200:
				return [m.get("name") for m in r.json().get("models", [])]
			return []
		except Exception:
			return []

	def _get_effective_model(self) -> str:
		"""Resolve model name, auto-detecting from available Ollama models if needed."""
		try:
			available = self.list_models()
			if not available:
				return self.model
			if self.model in available:
				return self.model
			prefix = self.model.split(":")[0]
			matched = [m for m in available if m.startswith(prefix)]
			if matched:
				return matched[0]
			return available[0]
		except Exception:
			return self.model

	def generate(
		self, prompt: str, system_prompt: str | None = None, temperature: float = 0.1, **kwargs
	) -> str:
		"""Execute text completion via Ollama /api/generate."""
		model_to_use = self._get_effective_model()
		payload: dict[str, Any] = {
			"model": model_to_use,
			"prompt": prompt,
			"stream": False,
			"options": {"temperature": temperature},
		}
		if system_prompt:
			payload["system"] = system_prompt

		try:
			resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
			if resp.status_code == 200:
				return resp.json().get("response", "").strip()
			return ""
		except Exception:
			return ""

	def generate_structured(
		self, prompt: str, schema: type[BaseModel], system_prompt: str | None = None, **kwargs
	) -> BaseModel | None:
		"""Generate structured output validated against a Pydantic schema."""
		schema_json = json.dumps(schema.model_json_schema())
		enhanced_prompt = (
			f"{prompt}\n\n"
			f"You MUST return ONLY valid JSON matching this schema:\n"
			f"{schema_json}\n"
			f"Do not include any conversational preamble or markdown code fences."
		)

		payload: dict[str, Any] = {
			"model": self._get_effective_model(),
			"prompt": enhanced_prompt,
			"stream": False,
			"format": "json",
			"options": {"temperature": 0.0},
		}
		if system_prompt:
			payload["system"] = system_prompt

		try:
			resp = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=self.timeout)
			if resp.status_code != 200:
				return None

			raw_text = resp.json().get("response", "").strip()
			# Extract JSON block if surrounded by formatting
			if "{" in raw_text and "}" in raw_text:
				json_part = raw_text[raw_text.find("{") : raw_text.rfind("}") + 1]
				data = json.loads(json_part)
				return schema.model_validate(data)
			return None
		except Exception:
			return None
