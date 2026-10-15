import json
import pathlib
import subprocess
import traceback
from playwright.sync_api import sync_playwright

OUT=pathlib.Path.cwd()/"scratch"/"dash-010"
OUT.mkdir(parents=True,exist_ok=True)
BASE='http://localhost:8080'

def bench(code):
    r=subprocess.run(['docker','exec','-i','-w','/home/frappe/frappe-bench/sites','frappe_docker_main-backend-1','/home/frappe/frappe-bench/env/bin/python','-'],input=code,text=True,capture_output=True,encoding='utf-8')
    if r.returncode:raise RuntimeError('Local audit session operation failed: '+str(r.returncode))
    return r.stdout

sid=bench('''import frappe
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

out={'viewports':[],'javascript_errors':[],'http_errors':[],'summary_requests':0}
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True);context=browser.new_context(viewport={'width':1440,'height':1000})
  context.add_cookies([{'name':'sid','value':sid,'url':BASE}]);page=context.new_page()
  page.on('pageerror',lambda e:out['javascript_errors'].append(e.stack or str(e)))
  page.on('response',lambda r:out['http_errors'].append({'status':r.status,'path':r.url.split('?')[0].replace(BASE,'')}) if r.status>=400 else None)
  page.on('request',lambda r:out.update(summary_requests=out['summary_requests']+1) if 'get_owner_summary' in r.url else None)
  page.goto(BASE+'/desk/sarathiownertower',wait_until='domcontentloaded')
  page.wait_for_selector('.sod-home-filters',timeout=60000)
  page.wait_for_function('!!document.querySelector("select[name=company]")?.options.length && !document.querySelector("select[name=company]").disabled',timeout=60000)
  page.evaluate('window.host=[...document.querySelectorAll("*")].find(e=>e.sarathi_owner_dashboard)?.sarathi_owner_dashboard')
  out['multi_company_requires_selection']=page.locator('select[name=company]').input_value()==''
  page.evaluate('document.querySelector(".sod-home-filters").open=true')
  company=bench('import frappe\nfrappe.init("frontend");frappe.connect()\nprint(frappe.get_all("Project",filters={"company":["is","set"]},fields=["company"],limit=1)[0].company)\nfrappe.destroy()').strip()
  page.locator('select[name=company]').select_option(company)
  page.get_by_role('button',name='Apply filters',exact=False).click()
  page.wait_for_function('!!host.homeData && !host.homeBusy',timeout=60000)
  assert page.locator('.sod-home-intro h1').inner_text()=='Owner & Executive Dashboard'
  out['company_scope_matches']=page.evaluate('host.homeData.applied_filters.company===host.homeFilters.company')
  out['finance_cards']=page.locator('.sod-home-availability .sod-finance-kpis .sui-kpi').count()
  out['finance_values_available']=page.evaluate('host.homeData.finance?.data?.metrics.filter(m=>m.available).length')
  assert out['finance_cards']==8 and out['finance_values_available']==8
  out['sales_sections_available']=page.evaluate('host.homeData.sales.data.revenue.available && host.homeData.sales.data.backlog.available')
  assert out['sales_sections_available']
  page.wait_for_selector('.sod-sales-analytics .sui-chart svg',timeout=30000)
  out['native_chart_rendered']=True
  original_income=page.evaluate('host.homeData.sales.data.revenue.included_income')
  page.evaluate('host.homeFilters={...host.homeFilters,top_limit:1,page_length:1,backlog_page_length:1};host.refreshHomepage()')
  page.wait_for_function('host.homeData?.sales?.data?.applied_filters.top_limit===1 && !host.homeBusy',timeout=60000)
  out['top_limit_and_backlog_pagination']=page.evaluate('host.homeData.sales.data.revenue.top_customers.length===1 && host.homeData.sales.data.backlog.rows.length===1 && host.homeData.sales.data.backlog.has_next')
  assert out['top_limit_and_backlog_pagination']
  out['pagination_preserves_income']=page.evaluate('host.homeData.sales.data.revenue.included_income')==original_income
  page.evaluate('host.homeFilters={...host.homeFilters,start:1,backlog_start:1};host.refreshHomepage()')
  page.wait_for_function('host.homeData?.sales?.data?.applied_filters.start===1 && !host.homeBusy',timeout=60000)
  out['second_page_loaded']=page.evaluate('host.homeData.sales.data.revenue.rows[0].rank===2')
  assert out['second_page_loaded']
  page.evaluate('host.homeFilters={...host.homeFilters,start:0,backlog_start:0,page_length:25,backlog_page_length:25,top_limit:5};host.refreshHomepage()')
  page.wait_for_function('host.homeData?.sales?.data?.applied_filters.page_length===25 && !host.homeBusy',timeout=60000)

  for width,height in [(360,800),(390,844),(480,900),(767,1000),(768,1000),(1023,1000),(1024,1000),(1440,1000),(844,390)]:
   page.set_viewport_size({'width':width,'height':height});page.wait_for_timeout(200)
   metrics=page.evaluate('({width:innerWidth,page_scroll_width:document.documentElement.scrollWidth,records:document.querySelectorAll(".sod-homepage tbody tr").length})')
   assert metrics['page_scroll_width']<=width,metrics
   overflow=page.evaluate('Array.from(document.querySelectorAll(".sod-wrapper,.sod-main,.sod-homepage,.sod-sales-analytics,.sod-sales-backlog")).filter(node=>node.clientWidth && node.scrollWidth>node.clientWidth+1).map(node=>({class:node.className,width:node.clientWidth,scroll:node.scrollWidth}))')
   assert not overflow,overflow
   metrics['dashboard_container_overflow']=overflow
   out['viewports'].append(metrics)
   if width in [390,768,1440]:
    page.locator('.sod-sales-analytics > h2').evaluate('(node)=>node.scrollIntoView({block:"start"})')
    page.screenshot(path=str(OUT/('customer-sales-'+str(width)+'.png')),full_page=True)
    page.locator('.sod-sales-backlog > h3').evaluate('(node)=>node.scrollIntoView({block:"start"})')
    page.screenshot(path=str(OUT/('sales-backlog-'+str(width)+'.png')),full_page=True)
    if width==1440:
     page.locator('.sod-sales-analytics .sui-chart').evaluate('(node)=>node.scrollIntoView({block:"start"})')
     page.screenshot(path=str(OUT/'sales-trend-1440.png'),full_page=True)
  page.set_viewport_size({'width':390,'height':844})
  page.evaluate('document.querySelector(".sod-home-filters").open=true')
  page.locator('input[name=from_date]').fill('2026-01-01');page.locator('input[name=to_date]').fill('2026-12-31')
  page.get_by_role('button',name='Apply filters',exact=False).click()
  page.wait_for_function('host.homeData.applied_filters.from_date==="2026-01-01" && !host.homeBusy',timeout=60000)
  out['date_filter_applied']=True
  page.evaluate('document.querySelector(".sod-home-filters").open=true')
  page.get_by_role('button',name='Reset filters',exact=False).click()
  page.wait_for_function('!host.homeData.applied_filters.from_date && !host.homeBusy',timeout=60000)
  out['reset_preserves_company']=page.evaluate('!!host.homeData.applied_filters.company')
  # Existing detail navigation remains functional; return retains applied Company.
  page.evaluate('host.goToPageByKey("projects")');page.wait_for_function('host.currentPage!==0 && !!host.activeData',timeout=60000)
  page.evaluate('host.selectPage(0)');page.wait_for_function('!!document.querySelector(".sod-homepage") && !host.homeBusy',timeout=60000)
  out['legacy_navigation_and_return']=page.evaluate('host.homeData.applied_filters.company===host.homeFilters.company')
  previous_rows=page.locator('.sod-homepage tbody tr').count()
  context.set_offline(True)
  page.evaluate('host.refreshHomepage(true)')
  page.wait_for_selector('.sui-state[data-state="offline"]',timeout=15000)
  out['offline_retains_same_scope_rows']=page.locator('.sod-homepage tbody tr').count()==previous_rows
  context.set_offline(False)
  page.evaluate('host.refreshHomepage()')
  page.wait_for_function('!!document.querySelector(".sod-homepage") && !host.homeBusy',timeout=60000)
  out['online_retry_recovered']=page.locator('.sui-state[data-state="offline"]').count()==0
  pattern='**/api/method/sarathi_owner.api.homepage.get_homepage*'
  page.route(pattern,lambda route:route.fulfill(status=403,content_type='application/json',body=json.dumps({'exc_type':'PermissionError'})))
  page.evaluate('host.refreshHomepage(true)')
  page.wait_for_selector('.sui-state[data-state="denied"]',timeout=15000)
  out['denied_discards_cached_records']=page.locator('.sod-homepage tbody tr').count()==0 and page.evaluate('host.homeData===null')
  page.unroute(pattern)
  context.set_offline(True)
  page.evaluate('host.refreshHomepage(true)')
  page.wait_for_selector('.sui-state[data-state="offline"]',timeout=15000)
  out['denied_records_do_not_reappear_offline']=page.locator('.sod-homepage tbody tr').count()==0
  context.set_offline(False)
  page.evaluate('host.refreshHomepage()')
  page.wait_for_function('!!host.homeData && !host.homeBusy',timeout=60000)
  out['injected_permission_denials']=[e for e in out['http_errors'] if e['status']==403 and 'homepage.get_homepage' in e['path']]
  out['http_errors']=[e for e in out['http_errors'] if e not in out['injected_permission_denials']]
  assert out['summary_requests']==0 and not out['javascript_errors'] and not out['http_errors'],out
  browser.close()
finally:
 bench('import frappe\nfrappe.init("frontend");frappe.connect()\nfrom frappe.sessions import delete_session\ndelete_session('+repr(sid)+')\nfrappe.db.commit();frappe.destroy()'.replace('\\n','\n'))
 out['audit_session_revoked']=True
 (OUT/'browser-results.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
 print(json.dumps(out,indent=2))
