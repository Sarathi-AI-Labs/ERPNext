"""Run in Linux: exercises deployment sequencing with a fake docker executable.

No daemon/socket, database or actual deployment is used by these tests.
"""
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

FAKE_DOCKER = """#!/usr/bin/env python3
import json,os,sys
a=sys.argv[1:]
with open(os.environ['MOCK_LOG'],'a') as f: f.write(json.dumps(a)+'\\n')
if 'config' in a and '--format' in a:
 print(json.dumps({'services':{'frontend':{'environment':{'FRAPPE_SITE_NAME_HEADER':'erp.sarathiailabs.com'}},'backend':{'environment':{'SARATHI_BASE_URL':'https://erp.sarathiailabs.com'}}}}))
elif 'list-apps' in a:
 print(json.dumps({'erp.sarathiailabs.com':os.environ['MOCK_APPS'].split(',')}))
elif a[0]=='inspect': print('sha256:previous-image')
elif 'ps' in a: print('existing-backend')
elif 'migrate' in a and os.environ.get('MOCK_FAIL')=='migrate': sys.exit(7)
elif 'execute' in a: print('{}')
"""


@unittest.skipUnless(os.name == "posix", "Deployment runner requires Linux bash")
class TestDeploy(unittest.TestCase):
	def run_deploy(self, apps, fail=""):
		with tempfile.TemporaryDirectory() as temp:
			root = Path(temp)
			scripts = root / "resources" / "sarathi"
			scripts.mkdir(parents=True)
			for name in ("deploy.sh", "environments.py"):
				shutil.copyfile(Path(__file__).parent / name, scripts / name)
			bin_path = root / "bin"
			bin_path.mkdir()
			docker = bin_path / "docker"
			docker.write_text(FAKE_DOCKER)
			docker.chmod(0o755)
			log = root / "commands.jsonl"
			env = dict(
				os.environ,
				PATH=str(bin_path) + os.pathsep + os.environ["PATH"],
				MOCK_LOG=str(log),
				MOCK_APPS=apps,
				MOCK_FAIL=fail,
			)
			result = subprocess.run(
				["bash", str(scripts / "deploy.sh")], env=env, text=True, capture_output=True
			)
			commands = [json.loads(line) for line in log.read_text().splitlines()]
			return result, commands

	def test_existing_apps_and_backup_order(self):
		result, commands = self.run_deploy("frappe,erpnext,sarathi_visibility,sarathi_owner")
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertFalse(any("install-app" in c for c in commands))

		def index(word):
			return next(i for i, command in enumerate(commands) if word in command)

		self.assertLess(index("backup"), index("migrate"))
		self.assertLess(index("stop"), index("backup"))
		self.assertEqual(commands[-1][-2:], ["set-maintenance-mode", "off"])

	def test_both_missing_apps_installed(self):
		result, commands = self.run_deploy("frappe,erpnext")
		self.assertEqual(result.returncode, 0, result.stderr)
		self.assertEqual(
			[c[-1] for c in commands if "install-app" in c], ["sarathi_visibility", "sarathi_owner"]
		)

	def test_failed_migration_keeps_maintenance(self):
		result, commands = self.run_deploy("frappe,erpnext,sarathi_visibility,sarathi_owner", "migrate")
		self.assertNotEqual(result.returncode, 0)
		self.assertIn("Maintenance remains enabled", result.stderr)
		self.assertFalse(any(c[-2:] == ["set-maintenance-mode", "off"] for c in commands))


if __name__ == "__main__":
	unittest.main()
