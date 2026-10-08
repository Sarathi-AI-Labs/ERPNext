"""Unit tests for ReadBackValidator."""

import unittest
from unittest.mock import MagicMock

from ERPNext_Agent.core.validator import ReadBackValidator


class TestReadBackValidator(unittest.TestCase):
	def setUp(self):
		self.mock_client = MagicMock()
		self.validator = ReadBackValidator(self.mock_client)

	def test_verify_status_match(self):
		self.mock_client.get_doc.return_value = {"success": True, "data": {"name": "DOC-001", "docstatus": 1}}
		res = self.validator.verify_document_status("Sales Order", "DOC-001", expected_docstatus=1)
		self.assertTrue(res["verified"])
		self.assertEqual(res["status_label"], "Submitted")

	def test_verify_status_mismatch(self):
		self.mock_client.get_doc.return_value = {"success": True, "data": {"name": "DOC-001", "docstatus": 0}}
		res = self.validator.verify_document_status("Sales Order", "DOC-001", expected_docstatus=1)
		self.assertFalse(res["verified"])
		self.assertIn("mismatch", res["reason"])

	def test_verify_stock_sufficient(self):
		self.mock_client.search_docs.return_value = {
			"success": True,
			"data": [{"actual_qty": 50.0, "reserved_qty": 10.0, "projected_qty": 40.0}],
		}
		res = self.validator.verify_stock_availability("ITEM-01", "Stores - S", required_qty=20.0)
		self.assertTrue(res["verified"])
		self.assertTrue(res["available"])

	def test_verify_stock_insufficient(self):
		self.mock_client.search_docs.return_value = {
			"success": True,
			"data": [{"actual_qty": 5.0, "reserved_qty": 0.0, "projected_qty": 5.0}],
		}
		res = self.validator.verify_stock_availability("ITEM-01", "Stores - S", required_qty=20.0)
		self.assertFalse(res["verified"])
		self.assertFalse(res["available"])
		self.assertIn("Insufficient stock", res["reason"])


if __name__ == "__main__":
	unittest.main()
