"""Read-only installed-version inventory, upgrade diff and upstream release checks.

Uses only Python's standard library. Does not install releases or migrate a site.
"""
import argparse
import json
import re
import subprocess
import urllib.request
from pathlib import Path


def write_json(path, data):
	path = Path(path)
	path.parent.mkdir(parents=True, exist_ok=True)
	path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def snapshot(container, site):
	code = f"""
import frappe, json
from sarathi_owner.api.module_catalog import inventory
frappe.init({site!r}); frappe.connect(); frappe.set_user('Administrator')
try:
    print('SARATHI_MANIFEST=' + json.dumps(inventory(), default=str))
finally:
    frappe.destroy()
"""
	result = subprocess.run(
		[
			"docker",
			"exec",
			"-i",
			"-w",
			"/home/frappe/frappe-bench/sites",
			container,
			"/home/frappe/frappe-bench/env/bin/python",
			"-",
		],
		input=code,
		text=True,
		encoding="utf-8",
		capture_output=True,
		check=True,
	)
	line = next(line for line in result.stdout.splitlines() if line.startswith("SARATHI_MANIFEST="))
	return json.loads(line.split("=", 1)[1])


def changes(before, after):
	return {
		"added": sorted(after.keys() - before.keys()),
		"removed": sorted(before.keys() - after.keys()),
		"changed": sorted(k for k in before.keys() & after.keys() if before[k] != after[k]),
	}


def compare(before, after):
	def entries(data):
		return {
			m["id"] + "/" + e["label"] + "/" + str(e["target"]): {k: v for k, v in e.items() if k != "id"}
			for m in data["modules"]
			for e in m["entries"]
		}

	fields_before = before.get("schema_manifest", {})
	fields_after = after.get("schema_manifest", {})
	schemas = changes(fields_before, fields_after)
	field_changes = {}
	for dt in schemas["changed"]:
		field_changes[dt] = changes(
			{f["name"]: f for f in fields_before[dt]["fields"]},
			{f["name"]: f for f in fields_after[dt]["fields"]},
		)
	return {
		"versions_before": before["versions"],
		"versions_after": after["versions"],
		"modules": changes(
			{m["id"]: m["label"] for m in before["modules"]}, {m["id"]: m["label"] for m in after["modules"]}
		),
		"entries": changes(entries(before), entries(after)),
		"doctypes": schemas,
		"fields": field_changes,
		"unsupported": [
			m["label"] + "/" + e["label"]
			for m in after["modules"]
			for e in m["entries"]
			if e["mode"] == "unsupported"
		],
	}


def releases(major):
	output = {}
	for app in ("frappe", "erpnext"):
		url = f"https://api.github.com/repos/frappe/{app}/releases?per_page=100"
		request = urllib.request.Request(
			url, headers={"User-Agent": "Sarathi-Integration-Audit", "Accept": "application/vnd.github+json"}
		)
		with urllib.request.urlopen(request, timeout=30) as response:
			data = json.load(response)
		candidates = [
			r
			for r in data
			if not r["prerelease"] and not r["draft"] and re.fullmatch(rf"v?{major}\.\d+\.\d+", r["tag_name"])
		]
		if not candidates:
			raise RuntimeError(
				f"No stable v{major} {app} release in the latest 100 releases; inspect upstream manually."
			)
		latest = max(candidates, key=lambda r: tuple(map(int, r["tag_name"].lstrip("v").split("."))))
		output[app] = {k: latest[k] for k in ("tag_name", "published_at", "html_url")}
	return output


def main():
	parser = argparse.ArgumentParser(description=__doc__)
	sub = parser.add_subparsers(dest="command", required=True)
	snap = sub.add_parser("snapshot")
	snap.add_argument("--container", default="frappe_docker_main-backend-1")
	snap.add_argument("--site", default="frontend")
	snap.add_argument("--output", required=True)
	diff = sub.add_parser("compare")
	diff.add_argument("before")
	diff.add_argument("after")
	diff.add_argument("--output", required=True)
	rel = sub.add_parser("releases")
	rel.add_argument("--major", type=int, default=16)
	rel.add_argument("--output", required=True)
	args = parser.parse_args()
	if args.command == "snapshot":
		result = snapshot(args.container, args.site)
	elif args.command == "compare":
		result = compare(
			json.loads(Path(args.before).read_text(encoding="utf-8")),
			json.loads(Path(args.after).read_text(encoding="utf-8")),
		)
	else:
		result = releases(args.major)
	write_json(args.output, result)
	print(f"Written: {args.output}")


if __name__ == "__main__":
	main()
