"""End-to-End Workflow Integration Tests for MasterERPNextAgent."""

import os
import unittest

from ERPNext_Agent.core.master_agent import MasterERPNextAgent


class TestE2EWorkflows(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		cls.agent = MasterERPNextAgent(container_name="frappe_docker_main-backend-1", site_name="frontend")

	def test_e2e_query_company(self):
		prompt = "What is the default currency of company SarathiAILabs?"
		result = self.agent.handle_request(prompt)

		# Check routing
		self.assertEqual(result["route"]["primary_module"], "Organization")
		self.assertEqual(result["route"]["action"], "QUERY")

		# Check execution
		exec_res = result.get("execution", {})
		self.assertTrue(exec_res.get("success"), f"Execution failed: {exec_res.get('error')}")
		self.assertEqual(exec_res.get("steps_executed"), 1)

		# Check audit log file created and populated
		audit_file = self.agent.audit.log_file
		self.assertTrue(os.path.isfile(audit_file), "Audit log file was not created")
		with open(audit_file, encoding="utf-8") as f:
			lines = f.readlines()
			self.assertGreater(len(lines), 0, "Audit log file is empty")

	def test_e2e_skill_context_loading(self):
		prompt = "Create a Work Order for 5 units of ITEM-TEST"
		result = self.agent.handle_request(prompt)
		self.assertEqual(result["route"]["primary_module"], "Manufacturing")
		self.assertIn("Manufacturing", result.get("message", ""))


if __name__ == "__main__":
	unittest.main()
