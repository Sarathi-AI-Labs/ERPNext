"""Dynamic On-Demand Skill Loader for ERPNext AI Agent.

Loads domain rules, field definitions, workflows, and few-shot examples for specific
modules on-demand to keep context sizes minimal and deterministic.
"""

import json
import os
from typing import Any, Dict, Optional


class SkillLoader:
	"""Manages lazy-loading and caching of module skill packages."""

	def __init__(self, agent_base_dir: str | None = None):
		if agent_base_dir is None:
			self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		else:
			self.base_dir = agent_base_dir

		self._cache: dict[str, dict[str, Any]] = {}

	def load_skill(self, module_name: str) -> dict[str, Any]:
		"""Load SKILL.md, rules.json, workflows.json, and examples.json for a module."""
		if module_name in self._cache:
			return self._cache[module_name]

		module_path = os.path.join(self.base_dir, module_name)
		if not os.path.isdir(module_path):
			raise FileNotFoundError(f"Skill directory not found for module '{module_name}' at {module_path}")

		skill_data: dict[str, Any] = {
			"module": module_name,
			"path": module_path,
			"instructions": "",
			"rules": {},
			"workflows": {},
			"examples": [],
		}

		# 1. Read SKILL.md
		skill_md_path = os.path.join(module_path, "SKILL.md")
		if os.path.isfile(skill_md_path):
			with open(skill_md_path, encoding="utf-8") as f:
				skill_data["instructions"] = f.read()

		# 2. Read rules.json
		rules_path = os.path.join(module_path, "rules.json")
		if os.path.isfile(rules_path):
			with open(rules_path, encoding="utf-8") as f:
				try:
					skill_data["rules"] = json.load(f)
				except Exception as e:
					skill_data["rules"] = {"error": f"Failed to parse rules.json: {e}"}

		# 3. Read workflows.json
		workflows_path = os.path.join(module_path, "workflows.json")
		if os.path.isfile(workflows_path):
			with open(workflows_path, encoding="utf-8") as f:
				try:
					skill_data["workflows"] = json.load(f)
				except Exception as e:
					skill_data["workflows"] = {"error": f"Failed to parse workflows.json: {e}"}

		# 4. Read examples.json
		examples_path = os.path.join(module_path, "examples.json")
		if os.path.isfile(examples_path):
			with open(examples_path, encoding="utf-8") as f:
				try:
					skill_data["examples"] = json.load(f)
				except Exception:
					skill_data["examples"] = []

		self._cache[module_name] = skill_data
		return skill_data

	def load_section(self, module_name: str, section_name: str) -> dict[str, Any]:
		"""Load section_info.json and SKILL.md for a specific submodule section."""
		cache_key = f"{module_name}::{section_name}"
		if cache_key in self._cache:
			return self._cache[cache_key]

		section_path = os.path.join(self.base_dir, module_name, section_name)
		if not os.path.isdir(section_path):
			return {}

		section_data: dict[str, Any] = {
			"module": module_name,
			"section": section_name,
			"path": section_path,
			"info": {},
			"instructions": "",
		}

		info_file = os.path.join(section_path, "section_info.json")
		if os.path.isfile(info_file):
			try:
				with open(info_file, encoding="utf-8") as f:
					section_data["info"] = json.load(f)
			except Exception:
				pass

		skill_file = os.path.join(section_path, "SKILL.md")
		if os.path.isfile(skill_file):
			try:
				with open(skill_file, encoding="utf-8") as f:
					section_data["instructions"] = f.read()
			except Exception:
				pass

		self._cache[cache_key] = section_data
		return section_data

	def get_section_for_doctype(self, module_name: str, doctype: str) -> dict[str, Any] | None:
		"""Find and load the section knowledge corresponding to a DocType."""
		from ERPNext_Agent.core.registry import SkillRegistry

		reg = SkillRegistry(self.base_dir)
		mapping = reg.get_section_for_doctype(doctype)
		if mapping and mapping[0].lower() == module_name.lower():
			sec = self.load_section(mapping[0], mapping[1])
			if sec:
				return sec

		module_path = os.path.join(self.base_dir, module_name)
		if not os.path.isdir(module_path):
			return None

		# Check direct folder match first
		direct_path = os.path.join(module_path, doctype)
		if os.path.isdir(direct_path):
			return self.load_section(module_name, doctype)

		# Scan subdirectories for section_info.json primary_doctypes
		for item in os.listdir(module_path):
			item_path = os.path.join(module_path, item)
			if os.path.isdir(item_path):
				sec = self.load_section(module_name, item)
				pri_dts = sec.get("info", {}).get("primary_doctypes", [])
				if doctype in pri_dts or doctype.lower() in [d.lower() for d in pri_dts]:
					return sec

		return None

	def get_prompt_context(self, module_names: list[str]) -> str:
		"""Build an optimized prompt injection string for the requested modules."""
		chunks = []
		for mod in module_names:
			skill = self.load_skill(mod)
			chunks.append(f"### SKILL: {mod}\n{skill.get('instructions', '')}")
			if skill.get("rules"):
				chunks.append(
					f"#### Validation Rules ({mod}):\n```json\n{json.dumps(skill['rules'], indent=2)}\n```"
				)
		return "\n\n".join(chunks)
