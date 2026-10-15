import json
import pathlib
import subprocess
from playwright.sync_api import sync_playwright

OUT = pathlib.Path.cwd() / "docs" / "project-delivery-evidence"
OUT.mkdir(parents=True, exist_ok=True)
BASE = 'http://localhost:8080'

def bench(code):
    r = subprocess.run(['docker', 'exec', '-i', '-w', '/home/frappe/frappe-bench/sites', 'frappe_docker_main-backend-1', '/home/frappe/frappe-bench/env/bin/python', '-'], input=code, text=True, capture_output=True, encoding='utf-8')
    if r.returncode:
        raise RuntimeError('Local audit session operation failed: ' + str(r.returncode))
    return r.stdout

sid = bench('''import frappe
from frappe.auth import LoginManager,CookieManager
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request
frappe.init('frontend');frappe.connect()
frappe.local.request=Request(EnvironBuilder(path='/',base_url='http://localhost:8080').get_environ())
frappe.local.cookie_manager=CookieManager();frappe.local.form_dict=frappe._dict();frappe.local.request_ip='127.0.0.1'
LoginManager().login_as('Administrator')
print('AUDIT_SESSION='+frappe.session.sid)
frappe.db.commit();frappe.destroy()
''').split('AUDIT_SESSION=')[1].splitlines()[0]

out = {'viewports': [], 'javascript_errors': [], 'http_errors': [], 'summary_requests': 0}
try:
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={'width': 1440, 'height': 1000})
        context.add_cookies([{'name': 'sid', 'value': sid, 'url': BASE}])
        page = context.new_page()
        page.on('pageerror', lambda e: out['javascript_errors'].append(e.stack or str(e)))
        page.on('response', lambda r: out['http_errors'].append({'status': r.status, 'path': r.url.split('?')[0].replace(BASE, '')}) if r.status >= 400 else None)
        page.on('request', lambda r: out.update(summary_requests=out['summary_requests'] + 1) if 'get_owner_summary' in r.url else None)
        page.goto(BASE + '/desk/sarathiownertower', wait_until='domcontentloaded')
        page.wait_for_selector('.sod-home-filters', timeout=60000)
        page.wait_for_function('!!document.querySelector("select[name=company]")?.options.length && !document.querySelector("select[name=company]").disabled', timeout=60000)
        page.evaluate('window.host=[...document.querySelectorAll("*")].find(e=>e.sarathi_owner_dashboard)?.sarathi_owner_dashboard')
        out['multi_company_requires_selection'] = page.locator('select[name=company]').input_value() == ''
        page.evaluate('document.querySelector(".sod-home-filters").open=true')
        company = bench('import frappe\nfrappe.init("frontend");frappe.connect()\nprint(frappe.get_all("Project",filters={"company":["is","set"]},fields=["company"],limit=1)[0].company)\nfrappe.destroy()').strip()
        page.locator('select[name=company]').select_option(company)
        page.get_by_role('button', name='Apply filters', exact=False).click()
        page.wait_for_function('!!host.homeData && !host.homeBusy', timeout=60000)
        out['company_scope_matches'] = page.evaluate('host.homeData.applied_filters.company===host.homeFilters.company')
        out['project_health_available'] = page.evaluate('host.homeData.project_health?.available')
        assert out['project_health_available']

        out['project_portfolio_counts'] = page.evaluate('host.homeData.project_health.data.projects.counts')
        out['delivery_counts'] = page.evaluate('host.homeData.project_health.data.deliveries.counts')
        out['project_rows'] = page.locator('.sod-project-portfolio tbody tr').count()
        out['delivery_rows'] = page.locator('.sod-project-deliveries tbody tr').count()

        for width, height in [(360, 800), (390, 844), (480, 900), (767, 1000), (768, 1000), (1023, 1000), (1024, 1000), (1440, 1000), (844, 390)]:
            page.set_viewport_size({'width': width, 'height': height})
            page.wait_for_timeout(200)
            metrics = page.evaluate('({width:innerWidth,page_scroll_width:document.documentElement.scrollWidth,records:document.querySelectorAll(".sod-homepage tbody tr").length})')
            assert metrics['page_scroll_width'] <= width, metrics
            overflow = page.evaluate('Array.from(document.querySelectorAll(".sod-wrapper,.sod-main,.sod-homepage,.sod-project-health,.sod-project-portfolio,.sod-project-deliveries")).filter(node=>node.clientWidth && node.scrollWidth>node.clientWidth+1).map(node=>({class:node.className,width:node.clientWidth,scroll:node.scrollWidth}))')
            assert not overflow, overflow
            metrics['dashboard_container_overflow'] = overflow
            out['viewports'].append(metrics)
            if width in [390, 768, 1440]:
                page.locator('.sod-project-health > h2').evaluate('(node)=>node.scrollIntoView({block:"start"})')
                page.screenshot(path=str(OUT / ('project-health-' + str(width) + '.png')), full_page=True)
                page.locator('.sod-project-deliveries > h3').evaluate('(node)=>node.scrollIntoView({block:"start"})')
                page.screenshot(path=str(OUT / ('project-deliveries-' + str(width) + '.png')), full_page=True)

        browser.close()
finally:
    bench('import frappe\nfrappe.init("frontend");frappe.connect()\nfrom frappe.sessions import delete_session\ndelete_session(' + repr(sid) + ')\nfrappe.db.commit();frappe.destroy()'.replace('\\n', '\n'))
    out['audit_session_revoked'] = True
    (OUT / 'browser-results.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
    print(json.dumps(out, indent=2))
