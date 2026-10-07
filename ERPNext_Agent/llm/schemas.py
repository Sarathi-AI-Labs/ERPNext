"""Pydantic Schemas for LLM Communication, Intent Classification, and Parameter Extraction."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class LLMIntentClassification(BaseModel):
	"""Structured intent classification returned by LLM."""

	action: str = Field(
		default="QUERY",
		description="Classified ERPNext action: CREATE, UPDATE, DELETE, SUBMIT, CANCEL, AMEND, QUERY, REPORT",
	)
	primary_module: str = Field(
		default="Organization",
		description="Target ERPNext module (e.g. Organization, Projects, Stock, Manufacturing, Selling, Buying, Accounting)",
	)
	target_doctype: str | None = Field(
		default=None,
		description="Target DocType (e.g. Company, Project, Customer, Supplier, Item, Work Order)",
	)
	secondary_doctypes: list[str] = Field(
		default_factory=list, description="Additional DocTypes detected for multi-entity compound requests"
	)
	confidence: float = Field(default=1.0, description="Confidence score from 0.0 to 1.0")
	reasoning: str | None = Field(default=None, description="Brief reasoning for classification")


class LLMParameterExtraction(BaseModel):
	"""Structured parameters extracted from natural language by LLM."""

	doctype: str = Field(description="Target DocType name")
	parameters: dict[str, Any] = Field(default_factory=dict, description="Extracted key-value parameters")
	unresolved_mentions: list[str] = Field(
		default_factory=list, description="Ambiguous or unresolved entity mentions"
	)


class LLMHealthStatus(BaseModel):
	"""Health check status of LLM backend."""

	provider: str
	available: bool
	base_url: str
	model: str
	latency_ms: float = 0.0
	error: str | None = None
