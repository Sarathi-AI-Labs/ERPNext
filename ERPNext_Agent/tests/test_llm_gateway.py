"""Tests for LLMGateway and Ollama LLM integration."""

import unittest

from ERPNext_Agent.llm.gateway import LLMGateway
from ERPNext_Agent.llm.schemas import LLMHealthStatus, LLMIntentClassification, LLMParameterExtraction


class TestLLMGateway(unittest.TestCase):
	"""Test suite for unified LLMGateway interface and fallback handling."""

	def setUp(self):
		self.gateway = LLMGateway()

	def test_health_check(self):
		"""Verify health check returns valid Pydantic model with latency."""
		status = self.gateway.health_check()
		self.assertIsInstance(status, LLMHealthStatus)
		self.assertIsInstance(status.available, bool)
		self.assertGreaterEqual(status.latency_ms, 0.0)

	def test_classify_intent_fallback_or_output(self):
		"""Verify intent classification returns structured model or graceful None."""
		res = self.gateway.classify_intent("Create a new company called Demo Corp")
		if self.gateway.is_available() and res:
			self.assertIsInstance(res, LLMIntentClassification)
			self.assertIn(res.action, ["CREATE", "UPDATE", "DELETE", "SUBMIT", "CANCEL", "QUERY", "REPORT"])
		else:
			self.assertTrue(res is None or isinstance(res, LLMIntentClassification))

	def test_extract_parameters_fallback_or_output(self):
		"""Verify parameter extraction returns structured model or graceful None."""
		res = self.gateway.extract_parameters("Company: Demo Corp, Abbr: DC", "Company")
		if self.gateway.is_available() and res:
			self.assertIsInstance(res, LLMParameterExtraction)
			self.assertEqual(res.doctype, "Company")
		else:
			self.assertTrue(res is None or isinstance(res, LLMParameterExtraction))


if __name__ == "__main__":
	unittest.main()
