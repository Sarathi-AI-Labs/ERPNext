"""Tests for AuditLogger immutable logging and data sanitization."""

import os
import unittest

from ERPNext_Agent.core.audit import AuditLogger


class TestAuditLogger(unittest.TestCase):
	"""Test suite for AuditLogger security sanitization and persistent logging."""

	def setUp(self):
		self.logger = AuditLogger()

	def test_sanitize_sensitive_fields(self):
		"""Verify password, token, and secret fields are masked."""
		raw_data = {
			"user": "gaurav@example.com",
			"password": "supersecretpassword123",
			"api_key": "xyz123",
			"auth_token": "token456",
			"nested": {"secret_key": "nestedsecret"},
		}
		sanitized = self.logger._sanitize(raw_data)
		self.assertEqual(sanitized["user"], "gaurav@example.com")
		self.assertEqual(sanitized["password"], "********")
		self.assertEqual(sanitized["api_key"], "********")
		self.assertEqual(sanitized["auth_token"], "********")
		self.assertEqual(sanitized["nested"]["secret_key"], "********")

	def test_log_event_and_persistence(self):
		"""Verify log_event appends valid JSONL record to disk."""
		event = self.logger.log_event(
			event_type="TEST_EVENT",
			tool_name="test_tool",
			inputs={"company_name": "Test Co"},
			output={"success": True},
			user="Administrator",
			doctype="Company",
		)
		self.assertIn("event_id", event)
		self.assertEqual(event["user"], "Administrator")
		self.assertEqual(event["doctype"], "Company")
		self.assertTrue(os.path.exists(self.logger.log_file))


if __name__ == "__main__":
	unittest.main()
