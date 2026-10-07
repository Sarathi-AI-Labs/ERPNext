"""Live Integration Tests for ERPNext Agent Tools against Docker Container."""

import unittest

from ERPNext_Agent.tools.client import FrappeClient
from ERPNext_Agent.tools.meta_tools import CheckPermissionTool, GetDocMetaTool
from ERPNext_Agent.tools.query_tools import GetCountTool, GetValueTool, SearchDocumentsTool


class TestLiveTools(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.client = FrappeClient(container_name="frappe_docker_main-backend-1", site_name="frontend")

	def test_live_search_company(self):
		tool = SearchDocumentsTool(self.client)
		res = tool.execute(doctype="Company", fields=["name", "abbr"], limit=5)
		self.assertTrue(res.get("success"), f"Search failed: {res.get('error')}")
		self.assertGreater(res.get("count", 0), 0)
		names = [d["name"] for d in res.get("data", [])]
		self.assertIn("SarathiAILabs", names)

	def test_live_get_value_company(self):
		tool = GetValueTool(self.client)
		res = tool.execute(
			doctype="Company", filters={"name": "SarathiAILabs"}, fieldname=["abbr", "default_currency"]
		)
		self.assertTrue(res.get("success"), f"GetValue failed: {res.get('error')}")
		data = res.get("data", {})
		self.assertEqual(data.get("abbr"), "S")
		self.assertEqual(data.get("default_currency"), "INR")

	def test_live_get_count_items(self):
		tool = GetCountTool(self.client)
		res = tool.execute(doctype="DocType")
		self.assertTrue(res.get("success"), f"GetCount failed: {res.get('error')}")
		self.assertGreater(res.get("count", 0), 100)

	def test_live_get_doc_meta_project_custom_fields(self):
		tool = GetDocMetaTool(self.client)
		res = tool.execute(doctype="Project")
		self.assertTrue(res.get("success"), f"GetDocMeta failed: {res.get('error')}")
		fieldnames = [f["fieldname"] for f in res.get("fields", [])]
		# Verify custom fields injected by Sarathi apps
		self.assertIn("custom_sarathi_manufacturing", fieldnames)
		self.assertIn("custom_sarathi_bom", fieldnames)

	def test_live_check_permission(self):
		tool = CheckPermissionTool(self.client)
		res = tool.execute(doctype="Company", perm_type="read", user="Administrator")
		self.assertTrue(res.get("success"), f"CheckPermission failed: {res.get('error')}")
		self.assertTrue(res.get("has_permission"))


if __name__ == "__main__":
	unittest.main()
