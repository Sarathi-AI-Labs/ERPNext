"""Presentation contract tests. Run directly with the existing Python Playwright installation.

No site, credentials, ERP records or new test dependency are required.
"""
import os
from pathlib import Path
import unittest
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

PUBLIC = Path(__file__).resolve().parents[1] / "public"


@unittest.skipUnless(sync_playwright, 'Optional local Playwright tooling is unavailable')
class SharedUIBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = getattr(cls.playwright, os.environ.get('SARATHI_UI_BROWSER', 'chromium')).launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={"width": 390, "height": 844})
        self.page.set_content('<main data-sarathi-ui></main>')
        self.page.add_style_tag(content=(PUBLIC / 'css/sarathi_ui.css').read_text(encoding='utf-8'))
        self.page.add_script_tag(content=(PUBLIC / 'js/sarathi_ui.js').read_text(encoding='utf-8'))
        self.page.evaluate('window.UI=frappe.sarathiUI; window.root=document.querySelector("main")')

    def tearDown(self):
        self.page.close()

    def test_values_are_text_and_missing_is_not_zero(self):
        self.page.evaluate('root.append(UI.kpi({label:"<b>Fixture</b>",value:null}),UI.kpi({label:"Zero fixture",value:0}),UI.kpi({label:"Failed fixture",value:5,error:true}))')
        self.assertEqual(self.page.locator('.sui-kpi-value').all_text_contents(), ['—', '0', '—'])
        self.assertEqual(self.page.locator('b').count(), 0)
        self.assertEqual(self.page.locator('button').count(), 0)

    def test_progress_and_original_status(self):
        result = self.page.evaluate('''() => {
          for(const value of [null,"",NaN,0,120]) root.append(UI.progress({value}));
          root.append(UI.status("Pending Review"));
          return {bars:root.querySelectorAll('[role=progressbar]').length,
            values:[...root.querySelectorAll('[role=progressbar]')].map(e=>e.getAttribute('aria-valuetext')),
            status:root.querySelector('.sui-status').textContent};
        }''')
        self.assertEqual(result, {'bars': 2, 'values': ['0%', '120%'], 'status': 'Pending Review'})

    def test_async_action_deduplicates_and_recovers(self):
        self.page.evaluate('''window.calls=0; root.append(UI.action({label:"Fixture action",onActivate:()=>{calls++;return new Promise(resolve=>window.finish=resolve)}}))''')
        self.page.get_by_role('button', name='Fixture action').click()
        self.page.evaluate('root.querySelector("button").click()')
        self.assertEqual(self.page.evaluate('calls'), 1)
        self.assertTrue(self.page.locator('button').is_disabled())
        self.page.evaluate('finish()')
        self.page.wait_for_function('!root.querySelector("button").disabled')
        self.assertIn('Done', self.page.locator('button').inner_text())

    def test_action_error_hides_exception_and_confirm_cancels(self):
        self.page.evaluate('''window.calls=0; root.append(UI.action({label:"Fail fixture",onActivate:()=>{throw Error("SECRET SQL TRACE")}}),UI.action({label:"Confirm fixture",confirm:()=>false,onActivate:()=>calls++}))''')
        self.page.get_by_role('button', name='Fail fixture').click()
        self.assertNotIn('SECRET', self.page.locator('main').inner_text())
        self.page.get_by_role('button', name='Confirm fixture').click()
        self.assertEqual(self.page.evaluate('calls'), 0)

    def test_filter_values_options_apply_reset_and_validation(self):
        self.page.evaluate('''window.applied=[]; window.form=UI.filterBar({fields:[{key:"fixture",label:"Fixture selector",type:"select",options:[{value:"one",label:"Option one"}]},{key:"query",label:"Fixture query"}],onApply:v=>applied.push(v),onReset:v=>applied.push(v),validate:v=>v.query==="bad"?"Choose another value":""});root.append(form)''')
        self.page.get_by_label('Fixture selector').select_option('one')
        self.page.get_by_label('Fixture query').fill('bad')
        self.page.get_by_role('button', name='Apply filters').click()
        self.assertEqual(self.page.evaluate('applied.length'), 0)
        self.page.get_by_label('Fixture query').fill('ok')
        self.page.get_by_role('button', name='Apply filters').click()
        self.assertEqual(self.page.evaluate('applied[0]'), {'fixture': 'one', 'query': 'ok'})
        self.page.evaluate('form.setOptions("fixture",[],"loading")')
        self.assertTrue(self.page.get_by_label('Fixture selector').is_disabled())
        self.page.get_by_role('button', name='Reset filters').click()
        self.assertEqual(self.page.get_by_label('Fixture query').input_value(), '')

    def test_all_states_and_read_only_retry(self):
        self.page.evaluate('''window.calls=0;for(const kind of ["loading","empty","unavailable","denied","error","stale","offline"])root.append(UI.state(kind));root.append(UI.state("error",{retry:()=>calls++,retryKind:"write"}),UI.state("error",{retry:()=>calls++,retryKind:"read"}))''')
        self.assertEqual(self.page.locator('button').count(), 1)
        self.page.get_by_role('button', name='Retry loading').click()
        self.assertEqual(self.page.evaluate('calls'), 1)

    def test_responsive_records_long_text_and_shop_floor_targets(self):
        self.page.evaluate('''const layout=UI.layout({title:"Component fixture",density:"shop-floor"});layout.content.append(UI.recordList({columns:[{key:"id",label:"Identifier"},{key:"status",label:"Status",render:UI.status}],rows:[{id:"LONG".repeat(90),status:"Blocked"}],rowActions:()=>[{label:"Fixture details",onActivate:()=>{}}]}));root.append(layout)''')
        for width in [360,390,480,767,768,1023,1024,1440]:
            self.page.set_viewport_size({'width': width, 'height': 900})
            self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), width)
            self.assertGreaterEqual(self.page.locator('button').bounding_box()['height'], 56)
        self.page.locator('button').focus()
        self.assertEqual(self.page.locator('button').evaluate('e=>getComputedStyle(e).outlineStyle'), 'solid')

    def test_legacy_disclosure_preserves_input_and_keyboard(self):
        self.page.evaluate('''root.innerHTML='<section class="sd-controls"><label>Fixture <input value="retained"></label></section><div role="button" tabindex="0" data-action="fixture">Open fixture</div>';window.calls=0;root.querySelector('[role=button]').onclick=()=>calls++;UI.enhance(root);UI.enhance(root)''')
        self.assertEqual(self.page.get_by_role('button', name='Filters').count(), 1)
        self.page.get_by_role('button', name='Filters').click()
        self.assertEqual(self.page.locator('input').input_value(), 'retained')
        self.page.get_by_role('button', name='Open fixture').press('Enter')
        self.assertEqual(self.page.evaluate('calls'), 1)

    def test_chart_resize_and_cleanup(self):
        self.page.evaluate('''window.draws=0;window.fixtureChart=UI.chart({title:"Fixture chart",render:el=>{el.textContent="Chart fixture";return {resize:()=>draws++}}});root.append(fixtureChart);fixtureChart.mount()''')
        self.page.wait_for_function('draws>0')
        self.page.evaluate('fixtureChart.dispose();window.savedDraws=draws')
        self.page.set_viewport_size({'width': 768, 'height': 900})
        self.page.wait_for_timeout(100)
        self.assertEqual(self.page.evaluate('draws'), self.page.evaluate('savedDraws'))

    def test_record_search_sort_pagination_callbacks(self):
        self.page.evaluate('''window.events=[];root.append(UI.recordList({label:"Fixture records",columns:[{key:"id",label:"Identifier",sortable:true}],rows:[{id:"Fixture row"}],onSearch:v=>events.push(v),onSort:k=>events.push(k),pagination:{label:"Fixture page",next:()=>events.push("next")}}))''')
        self.page.get_by_role('searchbox', name='Search Fixture records').fill('query')
        self.page.get_by_role('button', name='Sort by Identifier').click()
        self.page.get_by_role('button', name='Next page').click()
        self.assertEqual(self.page.evaluate('events'), ['query', 'id', 'next'])

    def test_unsafe_and_missing_actions_are_rejected(self):
        self.assertTrue(self.page.evaluate('''() => {try{UI.action({label:"Unsafe",href:"javascript:alert(1)"});return false}catch(_){return true}}'''))
        self.assertTrue(self.page.evaluate('''() => {try{UI.action({label:"No action"});return false}catch(_){return true}}'''))

    def test_disabled_action_and_keyboard_activation(self):
        self.page.evaluate('''window.calls=0;root.append(UI.action({label:"Disabled fixture",disabled:true,onActivate:()=>calls++}),UI.action({label:"Keyboard fixture",onActivate:()=>calls++}))''')
        self.page.evaluate('root.querySelector("button").click()')
        self.assertEqual(self.page.evaluate('calls'), 0)
        self.page.get_by_role('button', name='Keyboard fixture').press('Space')
        self.assertEqual(self.page.evaluate('calls'), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
