"""Abstract Base Provider for LLM Integrations in ERPNext AI Agent."""

from abc import ABC, abstractmethod
from typing import Optional

from pydantic import BaseModel


class BaseLLMProvider(ABC):
	"""Abstract interface that all LLM providers must implement."""

	@abstractmethod
	def is_available(self) -> bool:
		"""Check if the LLM provider service is healthy and available."""
		pass

	@abstractmethod
	def generate(
		self, prompt: str, system_prompt: str | None = None, temperature: float = 0.1, **kwargs
	) -> str:
		"""Generate text completion from prompt."""
		pass

	@abstractmethod
	def generate_structured(
		self, prompt: str, schema: type[BaseModel], system_prompt: str | None = None, **kwargs
	) -> BaseModel | None:
		"""Generate structured Pydantic object from prompt."""
		pass
