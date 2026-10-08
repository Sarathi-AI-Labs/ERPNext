"""Read-only browser smoke check. Requires Playwright and a Netscape session cookie file.

Usage: python resources/sarathi/browser_smoke.py --cookies cookies.txt
No credentials or business record values are written to the result.
"""
import argparse
import http.cookiejar
import json
import subprocess
from urllib.parse import urlsplit

from environments import resolve
from playwright.sync_api import sync_playwright


def main():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("--environment", choices=("local", "production"), default="local")
	parser.add_argument("--url", help="Override the selected environment URL (or SARATHI_BASE_URL)")
	parser.add_argument("--site", help="Site name for the optional realtime check")
	parser.add_argument("--cookies", required=True)
	parser.add_argument(
		"--realtime-container", help="Optional local backend for a payload-free live event check"
	)
	args = parser.parse_args()
	target = resolve(args.environment, args.url, args.site)
	args.url = target["url"]
	remote = urlsplit(args.url).hostname not in ("localhost", "127.0.0.1", "::1")
	results = []
	with sync_playwright() as playwright:
		browser = playwright.chromium.launch(headless=True)
		context = browser.new_context(viewport={"width": 1440, "height": 1000})
		jar = http.cookiejar.MozillaCookieJar(args.cookies)
		jar.load(ignore_discard=True, ignore_expires=True)
		context.add_cookies(
			[{"name": c.name, "value": c.value, "domain": c.domain, "path": c.path or "/"} for c in jar]
		)
		for route in ("sarathiownertower", "sarathicontroltower"):
			realtime_checked = False
			page = context.new_page()
			errors = []
			localhost_requests = []
			page.on("pageerror", lambda e: errors.append(str(e)))

			def check_host(url):
				if remote and urlsplit(url).hostname in ("localhost", "127.0.0.1", "::1"):
					localhost_requests.append(urlsplit(url).netloc)

			page.on("request", lambda r: check_host(r.url))
			page.on("websocket", lambda socket: check_host(socket.url))
			page.goto(args.url + "/desk/" + route, wait_until="domcontentloaded")
			page.wait_for_selector(".scm-launcher button", timeout=90000)
			page.locator(".scm-launcher button").click(force=True)
			page.wait_for_selector("[data-scm-index]", timeout=30000)
			page.locator("[data-scm-index]").filter(has_text="Invoicing").first.click()
			entry_count = page.locator("[data-scm-entry]").count()
			assert entry_count >= 24, f"Invoicing entries missing: {entry_count}"
			page.locator("[data-scm-entry]").filter(has_text="Sales Invoice").first.click()
			page.wait_for_selector("[data-scm-native]", timeout=30000)
			assert page.locator(".scm-table").count() == 1
			if page.locator("[data-scm-record]").count():
				page.locator("[data-scm-record]").first.click()
				page.wait_for_selector(".scm-fields", timeout=30000)
				assert (
					page.locator("[data-scm-detail]")
					.get_by_role("heading", name="Items", exact=False)
					.count()
				)
				page.locator("[data-scm-back]").click()
				page.wait_for_selector("[data-scm-search]", timeout=30000)
			if args.realtime_container:
				prop = "sarathi_owner_dashboard" if route == "sarathiownertower" else "sarathi_dashboard"
				page.evaluate(
					"""(prop) => {
                    const dashboard = [...document.querySelectorAll('*')].find(e => e[prop])[prop];
                    clearInterval(dashboard.moduleBrowser.timer);
                }""",
					prop,
				)
				code = f"import frappe; frappe.init({target['site']!r}); frappe.connect(); frappe.publish_realtime('sarathi_records_changed', {{}}, after_commit=False); frappe.destroy()"
				with page.expect_response(
					lambda r: "module_catalog.get_entry" in r.url, timeout=15000
				) as updated:
					subprocess.run(
						[
							"docker",
							"exec",
							"-w",
							"/home/frappe/frappe-bench/sites",
							args.realtime_container,
							"/home/frappe/frappe-bench/env/bin/python",
							"-c",
							code,
						],
						check=True,
						capture_output=True,
					)
				assert updated.value.ok
				realtime_checked = True
			page.locator("[data-scm-native]").click()
			frame = page.frame_locator(".scm-native-frame")
			frame.get_by_role("button", name="Add Sales Invoice", exact=False).wait_for(timeout=45000)
			assert urlsplit(page.url).path == "/desk/" + route
			# Specialized report executes its actual ERPNext implementation inside the frame.
			with page.expect_response(
				lambda r: "frappe.desk.query_report.run" in r.url, timeout=60000
			) as report_result:
				page.locator("[data-scm-entry]").filter(has_text="Accounts Receivable").first.click()
			assert report_result.value.ok
			assert isinstance(report_result.value.json().get("message", {}).get("result"), list)
			page.wait_for_selector(".scm-native-frame", timeout=30000)
			frame = page.locator(".scm-native-frame").element_handle().content_frame()
			frame.wait_for_function(
				'window.frappe?.query_report?.report_name === "Accounts Receivable"', timeout=45000
			)
			frame.wait_for_function("window.frappe.query_report.filters?.length > 0", timeout=30000)
			assert frame.evaluate("frappe.query_report.ignore_prepared_report")
			assert urlsplit(page.url).path == "/desk/" + route
			if route == "sarathiownertower":
				page.locator(".scm-dialog .btn-modal-close").click()
				page.wait_for_selector(".scm-dialog", state="detached")
				page.locator('#sod-nav [data-key="invoicing"]').evaluate("(el) => el.click()")
				page.wait_for_selector("[data-quick-detail]", timeout=30000)
				assert page.locator("[data-quick-detail]").count() == 8
				page.locator("[data-quick-detail]").first.click(force=True)
				page.wait_for_selector("[data-scm-search]", timeout=30000)
				assert urlsplit(page.url).path == "/desk/" + route
			assert not errors, errors
			assert not localhost_requests, "Production attempted localhost requests"
			results.append(
				{
					"dashboard": route,
					"invoicing_entries": entry_count,
					"record_preview": True,
					"native_list": True,
					"native_report": True,
					"quick_action_checked": route == "sarathiownertower",
					"realtime_event_checked": realtime_checked,
					"origin": args.url,
					"localhost_requests": localhost_requests,
					"parent_navigation_preserved": True,
					"javascript_errors": errors,
				}
			)
			page.close()
		browser.close()
	print(json.dumps(results, indent=2))


if __name__ == "__main__":
	main()
