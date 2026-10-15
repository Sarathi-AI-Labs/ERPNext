"""Manual local HTTP security smoke check. No credentials/cookies are printed.

Uses existing business records, temporarily creates a native test User and User
Permissions, then deletes them and the test session. Requires the local Docker site.
"""
import json
from pathlib import Path
import subprocess
import urllib.error
import urllib.parse
import urllib.request

BASE = 'http://localhost:8080'
PREFIX = '/api/method/sarathi_owner.api.sales_analytics.'


def bench(code):
    result = subprocess.run(['docker', 'exec', '-i', '-w', '/home/frappe/frappe-bench/sites',
        'frappe_docker_main-backend-1', '/home/frappe/frappe-bench/env/bin/python', '-'],
        input=code, text=True, capture_output=True, encoding='utf-8')
    if result.returncode:
        raise RuntimeError('Local audit setup/cleanup failed; inspect server logs privately.')
    return result.stdout


def main():
    context = None
    results = {'checks': []}
    try:
        context = json.loads(bench('''import frappe,json
from frappe.auth import LoginManager,CookieManager
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request
frappe.init('frontend');frappe.connect();frappe.set_user('Administrator')
projects=frappe.get_all('Project',fields=['name','company','customer'],order_by='name asc',limit=50)
selected=next(p for p in projects if p.company and p.customer)
other=next(p for p in projects if p.name!=selected.name)
user='dash010-http-'+frappe.generate_hash(length=10)+'@example.invalid'
frappe.get_doc(dict(doctype='User',email=user,first_name='DASH010 HTTP audit',send_welcome_email=0,
 roles=[dict(role=r) for r in ['Sarathi Owner','Accounts Manager','Accounts User','Projects User','Sales User','Stock User']])).insert()
for dt,name in [('Company',selected.company)]:
 frappe.get_doc(dict(doctype='User Permission',user=user,allow=dt,for_value=name,apply_to_all_doctypes=1)).insert()
frappe.local.request=Request(EnvironBuilder(path='/',base_url='http://localhost:8080').get_environ())
frappe.local.cookie_manager=CookieManager();frappe.local.form_dict=frappe._dict();frappe.local.request_ip='127.0.0.1'
LoginManager().login_as(user)
print(json.dumps(dict(user=user,sid=frappe.session.sid,company=selected.company,project=selected.name,other_project=other.name)))
frappe.db.commit();frappe.destroy()
''').splitlines()[-1])

        def request(method, params, session=True, verb='GET'):
            encoded = urllib.parse.urlencode({k: json.dumps(v) if isinstance(v, dict) else v for k, v in params.items()})
            url = BASE + PREFIX + method + ('?' + encoded if verb == 'GET' else '')
            headers = {'Accept': 'application/json'}
            if session:
                headers['Cookie'] = 'sid=' + context['sid']
            if verb == 'POST':
                headers['Content-Type'] = 'application/x-www-form-urlencoded'
            req = urllib.request.Request(url, headers=headers, method=verb, data=encoded.encode() if verb == 'POST' else None)
            try:
                response = urllib.request.urlopen(req, timeout=30)
            except urllib.error.HTTPError as error:
                response = error
            payload = json.loads(response.read())
            return response.status, payload

        def check(label, method, params, expected, **kwargs):
            status, body = request(method, params, **kwargs)
            assert status == expected, (label, status, body.get("_server_messages"))
            # No traceback, SQL or sensitive internal exception details in error responses.
            if status >= 400:
                assert 'exc' not in body and 'exception' not in body, label
                assert 'Traceback' not in json.dumps(body), label
            results['checks'].append({'check': label, 'status': status, 'passed': True})
            return body.get('message')

        data=check('authorized sales analytics', 'get_sales_analytics', {'filters':{'company':context['company']}},200)
        assert data['revenue']['available'] and data['backlog']['available']
        check('unexpected query field','get_sales_analytics',{'filters':{'company':context['company']},'fields':'*'},417)
        check('identity filter injection','get_sales_analytics',{'filters':{'company':context['company'],'user':'Administrator'}},417)
        check('guest sales denied','get_sales_analytics',{'filters':{'company':context['company']}},403,session=False)
        status,_=request('get_sales_analytics',{'filters':{'company':context['company']}},verb='POST')
        assert status in (400,403)
        results['checks'].append({'check':'POST denied','status':status,'passed':True})
        bench('import frappe\nfrappe.init("frontend");frappe.connect();frappe.set_user("Administrator")\nu=frappe.get_doc("User",'+repr(context['user'])+')\nu.remove_roles("Sarathi Owner","Accounts Manager","Accounts User")\nfrappe.clear_cache(user=u.name);frappe.db.commit();frappe.destroy()')
        check('direct API denied after owner role removal','get_sales_analytics',{'filters':{'company':context['company']}},403)
    finally:
        if context:
            bench('''import frappe
from frappe.sessions import delete_session
frappe.init('frontend');frappe.connect();frappe.set_user('Administrator')
delete_session(''' + repr(context['sid']) + ''')
user=''' + repr(context['user']) + '''
frappe.delete_doc('User',user)
frappe.clear_cache(user=user)
frappe.db.commit()
assert not frappe.db.exists('User',user)
assert not frappe.db.exists('User Permission',{'user':user})
frappe.destroy()
''')
            results['temporary_user_permissions_and_session_removed'] = True
        output = Path('scratch/dash-010/http-results.json')
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(results, indent=2), encoding='utf-8')
        print(json.dumps(results, indent=2))


if __name__ == '__main__':
    main()
