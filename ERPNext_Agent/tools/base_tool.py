"""Base Tool Contract for ERPNext / Frappe Agent Tools.

Ensures all tools have structured parameter schemas, controlled execution,
permission checking, and standardized output format.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseTool(ABC):
	"""Abstract Base Class for all controlled Frappe / ERPNext Agent tools."""

	name: str = ""
	description: str = ""
	parameters_schema: dict[str, Any] = {}

	def __init__(self, client: Any = None):
		self.client = client

	@abstractmethod
	def execute(self, **kwargs) -> dict[str, Any]:
		"""Execute the tool operation against Frappe/ERPNext.

		Returns a standardized dictionary:
		{
		    "success": bool,
		    "data": Any,
		    "error": Optional[str],
		    "doctype": Optional[str],
		    "name": Optional[str]
		}
		"""
		pass

	def validate_inputs(self, kwargs: dict[str, Any]) -> None:
		"""Validate input arguments against parameters_schema."""
		required = self.parameters_schema.get("required", [])
		for field in required:
			if field not in kwargs or kwargs[field] is None:
				raise ValueError(f"Tool '{self.name}' missing mandatory argument: '{field}'")
