import json
import pathlib
import subprocess
import traceback
from playwright.sync_api import sync_playwright

OUT=pathlib.Path.cwd()/"scratch"/"dash-005"
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
out={'user':'Administrator','routes':[],'javascript_errors':[],'http_errors':[],'blocked_mutations':[]}
try:
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True)
        context=browser.new_context(viewport={'width':1440,'height':1000})
        context.add_cookies([{'name':'sid','value':sid,'url':BASE}])
        page=context.new_page()
        page.on('pageerror',lambda e:out['javascript_errors'].append({'route':page.url.split('?')[0], 'width':page.viewport_size['width'], 'stack':e.stack}))
        page.on('response',lambda r:out['http_errors'].append({'status':r.status,'path':r.url.split('?')[0].replace(BASE,'')}) if r.status>=400 else None)
        def guard(route):
            request=route.request
            if any(x in request.url for x in ['clear_owner_cache','associate_customer','agent_chat.send_message','control_tower.update_','control_tower.sync_','recalculate_progress','frappe.client.insert','frappe.client.save','frappe.client.submit','frappe.desk.form.save']):
                out['blocked_mutations'].append(request.url.split('?')[0].replace(BASE,''));route.abort()
            else:route.continue_()
        page.route('**/api/method/**',guard)
        for route,prop,root in [('sarathiownertower','sarathi_owner_dashboard','.sod-wrapper'),('sarathicontroltower','sarathi_dashboard','.sd-dashboard')]:
            row={'route':route,'viewports':[]}
            out['routes'].append(row)
            try:
                response=page.goto(BASE+'/desk/'+route,wait_until='domcontentloaded',timeout=60000)
                row['http_status']=response.status
                page.wait_for_function('(prop)=>[...document.querySelectorAll("*")].some(e=>e[prop])',arg=prop,timeout=60000)
                page.evaluate('(prop)=>window.auditHost=[...document.querySelectorAll("*")].find(e=>e[prop])[prop]',prop)
                page.wait_for_function('auditHost.activeData || auditHost.data',timeout=60000)
                row['data_received']=True
                row['views']=page.evaluate('auditHost.pagesConfig?.map(x=>x[3]) || Object.keys(auditHost.tabs || {})')
                row['initial_data_keys']=page.evaluate('Object.keys(auditHost.activeData || auditHost.data || {})')
                # Dismiss no business workflow: remove onboarding overlay only in this test DOM.
                row['onboarding_overlay_present']=page.locator('.onboarding-widget').count()>0
                page.evaluate('document.querySelector(".onboarding-widget")?.remove()')
                for width,height in [(360,800),(390,844),(480,900),(767,1000),(768,1000),(1023,1000),(1024,1000),(1440,1000),(844,390)]:
                    page.set_viewport_size({'width':width,'height':height})
                    page.wait_for_timeout(1200)
                    metrics=page.evaluate('''(selector)=>{
                      const root=document.querySelector(selector), w=innerWidth;
                      const visible=e=>{let r=e.getBoundingClientRect(),s=getComputedStyle(e);return r.width&&r.height&&s.visibility!=='hidden'&&s.display!=='none';};
                      const rect=root.getBoundingClientRect();
                      const elements=[...root.querySelectorAll('*')].filter(visible);
                      const outside=elements.filter(e=>{let r=e.getBoundingClientRect();return r.right>w+2||r.left< -2}).map(e=>({tag:e.tagName,cls:typeof e.className==='string'?e.className:'svg',width:Math.round(e.getBoundingClientRect().width)})).slice(0,12);
                      const controls=elements.filter(e=>e.matches('button,input,select,[role="button"]'));
                      return {viewport:w,page_scroll_width:document.documentElement.scrollWidth,root_width:Math.round(rect.width),root_scroll_width:root.scrollWidth,outside_elements:outside,small_control_examples:controls.filter(e=>{let r=e.getBoundingClientRect();return r.width<44||r.height<44}).slice(0,8).map(e=>({tag:e.tagName,cls:e.className,w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height})),small_controls:controls.filter(e=>{let r=e.getBoundingClientRect();return r.width<44||r.height<44}).length,visible_controls:controls.length,charts:root.querySelectorAll('svg').length,text_length:root.innerText.length};
                    }''',root)
                    metrics['height']=height
                    row['viewports'].append(metrics)
                    page.screenshot(path=str(OUT/(route+'-'+str(width)+'.png')),full_page=True)
                row['shared_ui_loaded']=page.evaluate('!!frappe.sarathiUI && !!auditHost.root.dataset.hasOwnProperty("sarathiUi")')
                page.set_viewport_size({'width':390,'height':844})
                row['phone_kpi_columns']=page.locator('#sod-kpi-cards-grid' if route=='sarathiownertower' else '[data-kpis]').evaluate('e=>getComputedStyle(e).gridTemplateColumns')
                disclosure=page.get_by_role('button',name='Filters',exact=True)
                disclosure.click()
                row['filters_expanded']=disclosure.get_attribute('aria-expanded')=='true'
                selected=page.locator('#sod-filter-status' if route=='sarathiownertower' else '[data-filter="status"]')
                if selected.count():
                    before=selected.input_value();disclosure.click();disclosure.click();row['filters_preserved']=before==selected.input_value()
                disclosure.click()
                card=page.locator('#sod-kpi-cards-grid [role="button"]' if route=='sarathiownertower' else '[data-kpis] button').first
                card.press('Enter')
                page.wait_for_timeout(1800)
                row['keyboard_drilldown_opened']=page.locator('#sod-stage-overlay.show' if route=='sarathiownertower' else '.modal.show').count()>0
                page.screenshot(path=str(OUT/(route+'-drilldown-390.png')),full_page=True)
                if route=='sarathiownertower':
                    page.locator('#sod-modal-close').click()
                else:
                    page.keyboard.press('Escape')
                # Exercise a read-only operational subview, then inspect responsive tables.
                if route=='sarathicontroltower':
                    page.set_viewport_size({'width':390,'height':844})
                    page.evaluate('auditHost.tab="production";auditHost.renderTabs();auditHost.renderContent()')
                    page.wait_for_timeout(1800)
                    row['production_tab_rendered']=page.locator('[data-content]').inner_text().__len__()>0
                    page.screenshot(path=str(OUT/'production-tab-390.png'),full_page=True)
                print(json.dumps({'route':route,'data_received':row.get('data_received',False),'viewports':[(x['viewport'],x['page_scroll_width']) for x in row['viewports']]}),flush=True)
            except Exception as e:
                row['failure_type']=type(e).__name__
                row['failure']=str(e)[:600]
                print(json.dumps({'route':route,'failure_type':type(e).__name__}),flush=True)
        page.evaluate('frappe.set_route("List","Company")')
        page.wait_for_timeout(1800)
        out['standard_page_unmarked']=page.locator('[data-sarathi-ui]:visible').count()==0
        browser.close()
except Exception as e:
    out['fatal_type']=type(e).__name__
    out['fatal']=str(e)[:600]
finally:
    try:
        bench('import frappe\nfrappe.init("frontend");frappe.connect()\nfrom frappe.sessions import delete_session\ndelete_session('+repr(sid)+')\nfrappe.db.commit();frappe.destroy()')
        out['audit_session_revoked']=True
    except Exception:out['audit_session_revoked']=False
    (OUT/'browser-results.json').write_text(json.dumps(out,indent=2),encoding='utf-8')
    print(json.dumps({'errors':out['javascript_errors'],'http_errors':out['http_errors'],'revoked':out.get('audit_session_revoked')}))
