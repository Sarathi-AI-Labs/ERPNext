import os
import unittest
from unittest.mock import patch

from environments import origin, resolve


class TestEnvironments(unittest.TestCase):
	def setUp(self):
		self.env = patch.dict(os.environ, {}, clear=True)
		self.env.start()
		self.addCleanup(self.env.stop)

	def test_both_targets(self):
		self.assertEqual(resolve("local")["url"], "http://localhost:8080")
		self.assertEqual(resolve("production")["url"], "https://erp.sarathiailabs.com")
		self.assertEqual(resolve("production")["site"], "erp.sarathiailabs.com")

	def test_desk_url_normalized(self):
		self.assertEqual(origin("https://erp.sarathiailabs.com/desk/"), "https://erp.sarathiailabs.com")

	def test_explicit_override_precedes_environment(self):
		os.environ["SARATHI_BASE_URL"] = "https://staging.example.com"
		self.assertEqual(resolve("production")["url"], "https://staging.example.com")
		self.assertEqual(
			resolve("production", "https://erp.sarathiailabs.com")["url"], "https://erp.sarathiailabs.com"
		)

	def test_invalid_and_insecure_targets(self):
		for value in (
			"ftp://example.com",
			"https://user:pass@example.com",
			"https://example.com/desk/customer",
			"https://example.com?secret=1",
		):
			with self.assertRaises(ValueError):
				origin(value)
		with self.assertRaises(ValueError):
			resolve("production", "http://erp.sarathiailabs.com")
