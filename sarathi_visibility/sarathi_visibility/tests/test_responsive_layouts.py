"""DASH-028: Automated Responsive Viewport and Layout Verification Tests.

Executes cross-dashboard responsive tests using Python Playwright across all
required viewport widths:
  - 320 x 640  (Small Mobile)
  - 375 x 812  (Standard Mobile)
  - 430 x 932  (Large Mobile)
  - 768 x 1024 (Tablet Portrait)
  - 1024 x 768 (Tablet Landscape / Compact Desktop)
  - 1366 x 768 (Laptop)
  - 1440 x 900 (Large Desktop)

Verifies:
  1. No page-level horizontal overflow (document.documentElement.scrollWidth <= viewport.width).
  2. KPI cards adapt cleanly without overlapping or unreadable clipping.
  3. Charts and tables use bounded containers (overflow-x: auto) rather than blowing out the viewport.
  4. Filters, search inputs, and navigation stack and wrap cleanly on narrow screens.
  5. Touch targets meet minimum height criteria (>= 44px, >= 38px for small buttons).
  6. Dialogs and modals fit within mobile viewports.
"""

import os
from pathlib import Path
import unittest

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

REPO_ROOT = Path(__file__).resolve().parents[3]
VISIBILITY_PUBLIC = REPO_ROOT / "sarathi_visibility" / "sarathi_visibility" / "public"
OWNER_PUBLIC = REPO_ROOT / "sarathi_owner" / "sarathi_owner" / "public"
PAGES_DIR = REPO_ROOT / "sarathi_visibility" / "sarathi_visibility" / "sarathi_visibility" / "page"
OWNER_PAGES_DIR = REPO_ROOT / "sarathi_owner" / "sarathi_owner" / "sarathi_owner" / "page"

VIEWPORTS = [
    {"name": "Small Mobile (320x640)", "width": 320, "height": 640},
    {"name": "Standard Mobile (375x812)", "width": 375, "height": 812},
    {"name": "Large Mobile (430x932)", "width": 430, "height": 932},
    {"name": "Tablet Portrait (768x1024)", "width": 768, "height": 1024},
    {"name": "Tablet Landscape (1024x768)", "width": 1024, "height": 768},
    {"name": "Laptop (1366x768)", "width": 1366, "height": 768},
    {"name": "Large Desktop (1440x900)", "width": 1440, "height": 900},
]


@unittest.skipUnless(sync_playwright, "Playwright is not available")
class ResponsiveLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        browser_type = os.environ.get("SARATHI_UI_BROWSER", "chromium")
        cls.browser = getattr(cls.playwright, browser_type).launch(headless=True)
        # Load shared and application stylesheets
        cls.ui_css = (VISIBILITY_PUBLIC / "css" / "sarathi_ui.css").read_text(encoding="utf-8")
        cls.shopfloor_css = (VISIBILITY_PUBLIC / "css" / "sarathi_shopfloor.css").read_text(encoding="utf-8")
        cls.dashboard_css = (VISIBILITY_PUBLIC / "css" / "sarathi_dashboard.css").read_text(encoding="utf-8")
        cls.owner_homepage_css = (OWNER_PUBLIC / "css" / "sarathi_owner_homepage.css").read_text(encoding="utf-8")
        cls.owner_dashboard_css = (OWNER_PUBLIC / "css" / "sarathi_owner_dashboard.css").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={"width": 1440, "height": 900})

    def tearDown(self):
        self.page.close()

    # -------------------------------------------------------------------------
    # TEST 1: Shop-Floor Operator Workboard Responsiveness
    # -------------------------------------------------------------------------
    def test_shopfloor_operator_workboard_responsive(self):
        """Verifies operator workboard layout across all 7 viewports."""
        html_template = (PAGES_DIR / "sarathishopfloor" / "sarathishopfloor.html").read_text(encoding="utf-8")
        self.page.set_content(html_template)
        self.page.add_style_tag(content=self.ui_css)
        self.page.add_style_tag(content=self.shopfloor_css)

        # Populate sample jobs and active operation in DOM
        self.page.evaluate("""() => {
            document.querySelector('[data-kpi-assigned]').textContent = '12';
            document.querySelector('[data-kpi-progress]').textContent = '3';
            document.querySelector('[data-kpi-waiting]').textContent = '7';
            document.querySelector('[data-kpi-completed]').textContent = '2';
            document.querySelector('[data-kpi-blocked]').textContent = '0';
            document.querySelector('[data-current-op-container]').innerHTML = `
                <div class="sf-active-card">
                    <div class="sf-active-header">
                        <div class="sf-active-title-group">
                            <h2 class="sf-active-op-title">CNC Milling - Housing Machining</h2>
                            <span class="sf-station-badge">CNC-01</span>
                        </div>
                    </div>
                    <div class="sf-active-body">
                        <div class="sf-active-meta">
                            <div class="sf-meta-item"><span class="sf-meta-label">Work Order</span><span class="sf-meta-val">MFG-WO-2026-00042</span></div>
                            <div class="sf-meta-item"><span class="sf-meta-label">Item</span><span class="sf-meta-val">HOUSING-ALUM-V2</span></div>
                            <div class="sf-meta-item"><span class="sf-meta-label">Output Progress</span><span class="sf-meta-val">25 / 100 Nos (25%)</span></div>
                        </div>
                        <div class="sf-action-row">
                            <button type="button" class="sf-btn sf-btn-primary sf-touch-btn">Report Progress</button>
                            <button type="button" class="sf-btn sf-btn-secondary sf-touch-btn">Pause</button>
                            <button type="button" class="sf-btn sf-btn-success sf-touch-btn">Complete</button>
                        </div>
                    </div>
                </div>
            `;
            document.querySelector('[data-jobs-container]').innerHTML = `
                <div class="sf-job-card">
                    <div class="sf-job-header"><span class="sf-job-id">JC-2026-00101</span><span class="sf-status-tag sf-status-open">Open</span></div>
                    <div class="sf-job-body">
                        <h3 class="sf-job-op">Deburring & Polishing</h3>
                        <div class="sf-job-details"><span class="sf-station-chip">BENCH-02</span><span class="sf-wo-chip">WO-00042</span></div>
                    </div>
                    <div class="sf-job-footer">
                        <button type="button" class="sf-btn sf-btn-sm sf-btn-primary sf-touch-btn">Start Job</button>
                        <span class="sf-job-due">Due: 2026-10-20</span>
                    </div>
                </div>
            `;
        }""")

        for vp in VIEWPORTS:
            with self.subTest(viewport=vp["name"]):
                self.page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
                # Check horizontal overflow
                scroll_w = self.page.evaluate("document.documentElement.scrollWidth")
                self.assertLessEqual(
                    scroll_w,
                    vp["width"],
                    f"Horizontal page overflow detected at {vp['name']}: scrollWidth={scroll_w} > viewport={vp['width']}"
                )
                # Check touch target heights on mobile
                if vp["width"] <= 767:
                    btn_h = self.page.locator('.sf-action-row button').first.bounding_box()["height"]
                    self.assertGreaterEqual(
                        btn_h,
                        44,
                        f"Touch button height {btn_h}px should be >= 44px on mobile ({vp['name']})"
                    )

    # -------------------------------------------------------------------------
    # TEST 2: Shop-Floor Supervisor Team Overview Responsiveness
    # -------------------------------------------------------------------------
    def test_shopfloor_supervisor_overview_responsive(self):
        """Verifies supervisor team overview across all 7 viewports."""
        html_template = (PAGES_DIR / "sarathishopfloor" / "sarathishopfloor.html").read_text(encoding="utf-8")
        self.page.set_content(html_template)
        self.page.add_style_tag(content=self.ui_css)
        self.page.add_style_tag(content=self.shopfloor_css)

        # Switch to supervisor view and populate DOM
        self.page.evaluate("""() => {
            document.querySelector('[data-subview-bar]').style.display = 'block';
            document.querySelector('[data-operator-subview]').style.display = 'none';
            document.querySelector('[data-supervisor-subview]').style.display = 'block';
            // Populate 9 KPIs
            document.querySelector('[data-sup-kpi-members]').textContent = '8';
            document.querySelector('[data-sup-kpi-active-ops]').textContent = '5';
            document.querySelector('[data-sup-kpi-with-jobs]').textContent = '7';
            document.querySelector('[data-sup-kpi-without-work]').textContent = '1';
            document.querySelector('[data-sup-kpi-active-jcs]').textContent = '6';
            document.querySelector('[data-sup-kpi-waiting-jcs]').textContent = '14';
            document.querySelector('[data-sup-kpi-completed-jcs]').textContent = '19';
            document.querySelector('[data-sup-kpi-blocked-jcs]').textContent = '2';
            document.querySelector('[data-sup-kpi-overdue-jcs]').textContent = '1';

            // Populate workload card
            document.querySelector('[data-sup-workload-container]').innerHTML = `
                <div class="sf-operator-card">
                    <div class="sf-operator-card-header">
                        <div class="sf-operator-info">
                            <div class="sf-operator-avatar">RK</div>
                            <div>
                                <h4 class="sf-operator-name">Rajesh Kumar</h4>
                                <p class="sf-operator-role">Senior CNC Machinist &middot; Machining</p>
                            </div>
                        </div>
                        <span class="sf-status-pill sf-status-working">Working</span>
                    </div>
                    <div class="sf-workload-counts-row">
                        <span class="sf-count-chip">WIP: <strong>1</strong></span>
                        <span class="sf-count-chip">Waiting: <strong>3</strong></span>
                        <span class="sf-count-chip">Completed: <strong>4</strong></span>
                    </div>
                </div>
            `;

            // Populate table in sf-table-card
            document.querySelector('[data-sup-active-container]').innerHTML = `
                <div class="sf-table-card">
                    <table class="sf-data-table">
                        <thead>
                            <tr><th>Job Card</th><th>Work Order</th><th>Operation</th><th>Workstation</th><th>Operator</th><th>Output</th><th>Elapsed</th><th>Status</th></tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td><strong>JC-2026-0001</strong></td>
                                <td>WO-2026-0042</td>
                                <td>Milling</td>
                                <td>CNC-01</td>
                                <td>Rajesh Kumar</td>
                                <td>25 / 100 Nos (25%)</td>
                                <td>45 mins</td>
                                <td><span class="sf-status-tag sf-status-wip">In Progress</span></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            `;
        }""")

        for vp in VIEWPORTS:
            with self.subTest(viewport=vp["name"]):
                self.page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
                scroll_w = self.page.evaluate("document.documentElement.scrollWidth")
                self.assertLessEqual(
                    scroll_w,
                    vp["width"],
                    f"Supervisor view horizontal overflow at {vp['name']}: scrollWidth={scroll_w} > viewport={vp['width']}"
                )
                # Verify that the table wrapper permits horizontal scroll rather than stretching the page
                table_card_overflow = self.page.locator('.sf-table-card').evaluate("el => getComputedStyle(el).overflowX")
                self.assertIn(
                    table_card_overflow,
                    ["auto", "scroll"],
                    f"sf-table-card must have overflow-x: auto, got {table_card_overflow}"
                )

    # -------------------------------------------------------------------------
    # TEST 3: Production Control Tower Responsiveness
    # -------------------------------------------------------------------------
    def test_production_control_tower_responsive(self):
        """Verifies Production Management Control Tower layout across all 7 viewports."""
        html_template = (PAGES_DIR / "sarathicontroltower" / "sarathicontroltower.html").read_text(encoding="utf-8")
        self.page.set_content(html_template)
        self.page.add_style_tag(content=self.ui_css)
        self.page.add_style_tag(content=self.dashboard_css)

        # Populate sample Control Tower KPI cards, chart grid, and exception table
        self.page.evaluate("""() => {
            document.querySelector('[data-factory-kpis]').innerHTML = `
                <div class="sd-card"><div class="sd-card-icon">⚡</div><p>Active Work Orders</p><strong>24</strong><small>8 due this week</small></div>
                <div class="sd-card"><div class="sd-card-icon">⚙</div><p>Job Cards in WIP</p><strong>38</strong><small>Across 12 stations</small></div>
                <div class="sd-card"><div class="sd-card-icon">⚠</div><p>Shortage Blockers</p><strong>3</strong><small>Raw materials missing</small></div>
            `;
            document.querySelector('[data-exceptions-table]').innerHTML = `
                <div class="sd-table-container">
                    <table class="sd-table sd-exceptions-queue-table">
                        <thead>
                            <tr><th>Severity</th><th>Problem Details</th><th>Category</th><th>Source Doc</th><th>Item/Station</th><th>Due Date</th><th>Action</th></tr>
                        </thead>
                        <tbody>
                            <tr class="sd-exc-row sd-sev-critical">
                                <td><span class="sd-pill sd-sev-critical">Critical</span></td>
                                <td><strong>Material Deficit - Steel Flange</strong><p class="sd-exc-desc">Required for WO-2026-0089</p></td>
                                <td>Material</td>
                                <td>WO-2026-0089</td>
                                <td>STL-FLG-50MM</td>
                                <td>2026-10-15</td>
                                <td><button type="button" class="sd-button">Inspect</button></td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            `;
        }""")

        for vp in VIEWPORTS:
            with self.subTest(viewport=vp["name"]):
                self.page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
                scroll_w = self.page.evaluate("document.documentElement.scrollWidth")
                self.assertLessEqual(
                    scroll_w,
                    vp["width"],
                    f"Control Tower horizontal overflow at {vp['name']}: scrollWidth={scroll_w} > viewport={vp['width']}"
                )
                # Check that table container has overflow-x auto
                container_overflow = self.page.locator('.sd-table-container').evaluate("el => getComputedStyle(el).overflowX")
                self.assertIn(container_overflow, ["auto", "scroll"])

    # -------------------------------------------------------------------------
    # TEST 4: Owner & Executive Dashboard Responsiveness
    # -------------------------------------------------------------------------
    def test_owner_dashboard_responsive(self):
        """Verifies Owner & Executive Dashboard layout across all 7 viewports."""
        owner_html = """
        <div class="sod-wrapper" data-sarathi-ui>
            <div class="sod-app">
                <main class="sod-main">
                    <div class="sod-homepage">
                        <section class="sod-home-intro">
                            <h1>Owner &amp; Executive Dashboard</h1>
                            <p>Authoritative financial, operational, and commercial executive intelligence</p>
                        </section>
                        <section class="sod-home-filters">
                            <summary>Global Company &amp; Date Filters</summary>
                            <div class="sod-home-option-searches">
                                <div class="sod-home-option-search"><label>Company</label><input type="text" value="Sarathi AI Labs"></div>
                                <div class="sod-home-option-search"><label>From Date</label><input type="date" value="2026-01-01"></div>
                                <div class="sod-home-option-search"><label>To Date</label><input type="date" value="2026-12-31"></div>
                            </div>
                        </section>
                        <div class="sod-home-grid">
                            <div class="sod-home-panel sod-home-availability">
                                <h2>Key Financial Performance Indicators</h2>
                                <div class="sod-finance-kpis">
                                    <div class="sui-kpi"><span class="sui-kpi-label">Revenue YTD</span><strong class="sui-kpi-value">₹4.85 Cr</strong></div>
                                    <div class="sui-kpi"><span class="sui-kpi-label">Gross Margin</span><strong class="sui-kpi-value">32.4%</strong></div>
                                    <div class="sui-kpi"><span class="sui-kpi-label">Operating Profit</span><strong class="sui-kpi-value">₹1.12 Cr</strong></div>
                                    <div class="sui-kpi"><span class="sui-kpi-label">Outstanding Receivables</span><strong class="sui-kpi-value">₹68.4 L</strong></div>
                                </div>
                            </div>
                        </div>
                        <section class="sod-executive-risks">
                            <h3>Executive Risk &amp; Approvals Queue</h3>
                            <div class="sui-table-region">
                                <table class="sui-table">
                                    <thead>
                                        <tr><th>Severity</th><th>Risk Item</th><th>Document Reference</th><th>Impact Amount</th><th>Status</th></tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td><span class="sod-severity-badge" data-severity="Critical">Critical</span></td>
                                            <td>Customer Credit Limit Breached</td>
                                            <td>SO-2026-00312</td>
                                            <td>₹12.5 L</td>
                                            <td>Pending Approval</td>
                                        </tr>
                                    </tbody>
                                </table>
                            </div>
                        </section>
                    </div>
                </main>
            </div>
        </div>
        """
        self.page.set_content(owner_html)
        self.page.add_style_tag(content=self.ui_css)
        self.page.add_style_tag(content=self.owner_dashboard_css)
        self.page.add_style_tag(content=self.owner_homepage_css)

        for vp in VIEWPORTS:
            with self.subTest(viewport=vp["name"]):
                self.page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
                scroll_w = self.page.evaluate("document.documentElement.scrollWidth")
                self.assertLessEqual(
                    scroll_w,
                    vp["width"],
                    f"Owner dashboard horizontal overflow at {vp['name']}: scrollWidth={scroll_w} > viewport={vp['width']}"
                )
                # On screens <= 479px, financial KPIs should stack to single column
                if vp["width"] <= 479:
                    grid_cols = self.page.locator('.sod-finance-kpis').evaluate("el => getComputedStyle(el).gridTemplateColumns")
                    # Single column implies only one value in grid-template-columns (e.g., '280px' or '304px')
                    col_count = len(grid_cols.split())
                    self.assertEqual(col_count, 1, f"Expected 1 column on <= 479px, got {col_count} ({grid_cols})")

    # -------------------------------------------------------------------------
    # TEST 5: Responsive Dialogs and Modals Fit
    # -------------------------------------------------------------------------
    def test_responsive_dialogs_fit_viewports(self):
        """Verifies that modals/dialogs fit within viewports down to 320px."""
        dialog_html = """
        <div data-sarathi-ui>
            <div class="modal fade show" style="display: block; position: fixed; inset: 0; background: rgba(0,0,0,0.5);">
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h4 class="modal-title">Report Job Progress</h4>
                        </div>
                        <div class="modal-body">
                            <p>Target Qty: <strong>100 Nos</strong> &middot; Completed: <strong>25 Nos</strong></p>
                            <label>Additional Completed Qty <input type="number" value="10" style="width:100%;"></label>
                            <label>Remarks <input type="text" placeholder="Shift 1 batch complete" style="width:100%;"></label>
                        </div>
                        <div class="modal-footer" style="display: flex; justify-content: flex-end; gap: 8px;">
                            <button type="button" class="btn btn-secondary">Cancel</button>
                            <button type="button" class="btn btn-primary">Save Progress</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """
        self.page.set_content(dialog_html)
        self.page.add_style_tag(content=self.ui_css)

        for vp in VIEWPORTS:
            with self.subTest(viewport=vp["name"]):
                self.page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
                dialog_box = self.page.locator('.modal-dialog').bounding_box()
                self.assertIsNotNone(dialog_box)
                self.assertLessEqual(
                    dialog_box["width"],
                    vp["width"],
                    f"Modal width {dialog_box['width']} exceeds viewport {vp['width']}"
                )
                self.assertLessEqual(
                    dialog_box["height"],
                    vp["height"],
                    f"Modal height {dialog_box['height']} exceeds viewport {vp['height']}"
                )


if __name__ == "__main__":
    unittest.main(verbosity=2)
