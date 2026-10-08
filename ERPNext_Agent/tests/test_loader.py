"""Unit tests for SkillLoader."""

import unittest

from ERPNext_Agent.core.loader import SkillLoader


class TestSkillLoader(unittest.TestCase):
	def setUp(self):
		self.loader = SkillLoader()

	def test_load_all_13_modules(self):
		modules = [
			"Organization",
			"Stock",
			"Buying",
			"Selling",
			"Manufacturing",
			"Projects",
			"Subcontracting",
			"Quality",
			"Accounting",
			"Assets",
			"Framework",
			"Users and System",
			"ERPNext Settings",
		]
		for mod in modules:
			skill = self.loader.load_skill(mod)
			self.assertEqual(skill["module"], mod)
			self.assertTrue(len(skill["instructions"]) > 50, f"SKILL.md for {mod} was empty")
			self.assertIn(
				"doctypes",
				skill["rules"] or skill["rules"].get("doctypes", {}),
				f"rules.json for {mod} was invalid",
			)
			self.assertIn("transitions", skill["workflows"], f"workflows.json for {mod} was invalid")
			self.assertTrue(isinstance(skill["examples"], list), f"examples.json for {mod} was not a list")

	def test_context_formatting(self):
		ctx = self.loader.get_prompt_context(["Manufacturing", "Stock"])
		self.assertIn("SKILL: Manufacturing", ctx)
		self.assertIn("SKILL: Stock", ctx)


if __name__ == "__main__":
	unittest.main()
