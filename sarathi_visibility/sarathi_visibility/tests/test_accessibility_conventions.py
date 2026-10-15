"""DASH-029 Automated Accessibility and Status Conventions Test Suite.

Verifies WCAG 2.2 AA accessibility requirements across Sarathi dashboards:
- Keyboard navigation and high-visibility focus indicators.
- Text & status color contrast ratios (>= 4.5:1).
- Non-reliance on color alone (text labels + distinctive icons).
- Screen-reader semantics (table headers, aria labels, role attributes).
- Live region announcements for asynchronous updates.
- prefers-reduced-motion media query handling.
- Explicit unit of measure (UOM) identification in shop-floor reporting.
"""

import math
import os
from pathlib import Path
import re
import unittest

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

PUBLIC = Path(__file__).resolve().parents[1] / "public"
OWNER_PUBLIC = Path(__file__).resolve().parents[3] / "sarathi_owner" / "sarathi_owner" / "public"


def parse_rgb(rgb_str):
    """Parses rgb(r, g, b) or rgba(r, g, b, a) into normalized (r, g, b) floats [0, 1]."""
    m = re.search(r"rgba?\((\d+),\s*(\d+),\s*(\d+)", rgb_str)
    if not m:
        return (0.0, 0.0, 0.0)
    return tuple(float(x) / 255.0 for x in m.groups())


def relative_luminance(rgb):
    """Calculates relative luminance per WCAG 2.2 specification."""
    def adjust(c):
        return c / 12.92 if c <= 0.04045 else math.pow((c + 0.055) / 1.055, 2.4)
    r, g, b = (adjust(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(color1_rgb_str, color2_rgb_str):
    """Computes contrast ratio between two RGB color strings."""
    l1 = relative_luminance(parse_rgb(color1_rgb_str))
    l2 = relative_luminance(parse_rgb(color2_rgb_str))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


@unittest.skipUnless(sync_playwright, "Optional local Playwright tooling is unavailable")
class TestAccessibilityConventions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.browser = getattr(cls.playwright, os.environ.get("SARATHI_UI_BROWSER", "chromium")).launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.page = self.browser.new_page(viewport={"width": 1024, "height": 768})
        self.page.set_content('<main data-sarathi-ui></main>')
        self.page.add_style_tag(content=(PUBLIC / "css/sarathi_ui.css").read_text(encoding="utf-8"))
        if (PUBLIC / "css/sarathi_shopfloor.css").exists():
            self.page.add_style_tag(content=(PUBLIC / "css/sarathi_shopfloor.css").read_text(encoding="utf-8"))
        if (OWNER_PUBLIC / "css/sarathi_owner_homepage.css").exists():
            self.page.add_style_tag(content=(OWNER_PUBLIC / "css/sarathi_owner_homepage.css").read_text(encoding="utf-8"))
        self.page.add_script_tag(content=(PUBLIC / "js/sarathi_ui.js").read_text(encoding="utf-8"))
        self.page.evaluate('window.UI=frappe.sarathiUI; window.root=document.querySelector("main")')

    def tearDown(self):
        self.page.close()

    def test_status_badge_contrast_wcag_aa(self):
        """Verifies status badge text-to-background contrast exceeds WCAG 2.2 AA 4.5:1."""
        self.page.evaluate('''() => {
            const tones = ["danger", "warning", "success", "info", "neutral"];
            for (const tone of tones) {
                const el = document.createElement("span");
                el.className = "sui-status";
                el.dataset.tone = tone;
                el.textContent = tone.toUpperCase();
                root.appendChild(el);
            }
        }''')
        badges = self.page.locator('.sui-status').all()
        self.assertEqual(len(badges), 5)
        for badge in badges:
            color = badge.evaluate('el => getComputedStyle(el).color')
            bg = badge.evaluate('el => getComputedStyle(el).backgroundColor')
            tone = badge.evaluate('el => el.dataset.tone')
            cr = contrast_ratio(color, bg)
            self.assertGreaterEqual(cr, 4.5, f"Status tone '{tone}' contrast {cr:.2f}:1 is below 4.5:1 (color: {color}, bg: {bg})")

    def test_severity_badge_contrast_wcag_aa(self):
        """Verifies severity badge text-to-background contrast exceeds WCAG 2.2 AA 4.5:1."""
        self.page.evaluate('''() => {
            const severities = ["Critical", "High", "Medium", "Low", "Informational"];
            for (const s of severities) {
                root.appendChild(UI.severity(s));
            }
        }''')
        badges = self.page.locator('.sui-severity-badge').all()
        self.assertEqual(len(badges), 5)
        for badge in badges:
            color = badge.evaluate('el => getComputedStyle(el).color')
            bg = badge.evaluate('el => getComputedStyle(el).backgroundColor')
            sev = badge.evaluate('el => el.dataset.severity')
            cr = contrast_ratio(color, bg)
            self.assertGreaterEqual(cr, 4.5, f"Severity '{sev}' contrast {cr:.2f}:1 is below 4.5:1 (color: {color}, bg: {bg})")

    def test_status_and_severity_never_rely_on_color_alone(self):
        """Verifies badges provide visible icons and text labels (never color alone)."""
        res = self.page.evaluate('''() => {
            const st = UI.status("Critical Shortage");
            const sev = UI.severity("Critical");
            root.append(st, sev);
            const stIcon = getComputedStyle(st, '::before').content;
            const sevIcon = getComputedStyle(sev, '::before').content;
            return {
                statusText: st.textContent.trim(),
                statusIcon: st.dataset.icon,
                statusPseudoContent: stIcon,
                severityText: sev.textContent.trim(),
                severityIcon: sev.dataset.icon,
                severityPseudoContent: sevIcon
            };
        }''')
        self.assertIn("Critical Shortage", res["statusText"])
        self.assertTrue(bool(res["statusIcon"]))
        self.assertNotEqual(res["statusPseudoContent"], "none")
        self.assertIn("Critical", res["severityText"])
        self.assertTrue(bool(res["severityIcon"]))
        self.assertNotEqual(res["severityPseudoContent"], "none")

    def test_focus_visibility_indicators(self):
        """Verifies interactive elements have high-visibility focus-visible outlines (>= 3px solid)."""
        self.page.evaluate('''() => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.id = "test-btn";
            btn.textContent = "Action Button";
            const input = document.createElement("input");
            input.id = "test-input";
            input.type = "text";
            root.append(btn, input);
        }''')
        btn = self.page.locator('#test-btn')
        btn.focus()
        outline_width = btn.evaluate('el => getComputedStyle(el).outlineWidth')
        outline_style = btn.evaluate('el => getComputedStyle(el).outlineStyle')
        outline_color = btn.evaluate('el => getComputedStyle(el).outlineColor')
        self.assertEqual(outline_style, "solid")
        self.assertIn("3px", outline_width)
        # Outline color #2456b8 against white surface must be >= 4.5:1
        self.assertGreaterEqual(contrast_ratio(outline_color, "rgb(255, 255, 255)"), 4.5)

    def test_keyboard_activation_on_custom_interactive_controls(self):
        """Verifies [role=button] and tabs trigger on Enter and Space keys via sarathiUI.enhance."""
        self.page.evaluate('''() => {
            window.activated = [];
            const card = document.createElement("div");
            card.setAttribute("role", "button");
            card.tabIndex = 0;
            card.id = "custom-card";
            card.textContent = "Accessible Card";
            card.addEventListener("click", () => window.activated.push("custom-card"));

            const tab = document.createElement("div");
            tab.className = "sf-subview-tab";
            tab.tabIndex = 0;
            tab.id = "custom-tab";
            tab.textContent = "Accessible Tab";
            tab.addEventListener("click", () => window.activated.push("custom-tab"));

            root.append(card, tab);
            UI.enhance(root);
        }''')
        card = self.page.locator('#custom-card')
        card.focus()
        self.page.keyboard.press('Enter')
        self.assertEqual(self.page.evaluate('window.activated'), ['custom-card'])

        self.page.keyboard.press('Space')
        self.assertEqual(self.page.evaluate('window.activated'), ['custom-card', 'custom-card'])

        tab = self.page.locator('#custom-tab')
        tab.focus()
        self.page.keyboard.press('Enter')
        self.assertEqual(self.page.evaluate('window.activated'), ['custom-card', 'custom-card', 'custom-tab'])

    def test_screen_reader_semantics_for_tables_and_svgs(self):
        """Verifies tables receive th[scope=col] and SVGs are hidden from assistive technology."""
        self.page.evaluate('''() => {
            const table = document.createElement("table");
            table.innerHTML = `
                <thead>
                    <tr><th>Order</th><th>Status</th><th>Qty</th></tr>
                </thead>
                <tbody>
                    <tr><td>WO-001</td><td>Completed</td><td>100</td></tr>
                </tbody>
            `;
            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            root.append(table, svg);
            UI.enhance(root);
        }''')
        ths = self.page.locator('th').all()
        for th in ths:
            self.assertEqual(th.get_attribute('scope'), 'col')
        svg = self.page.locator('svg')
        self.assertEqual(svg.get_attribute('aria-hidden'), 'true')
        self.assertEqual(svg.get_attribute('focusable'), 'false')

    def test_accessible_charts_with_tabular_alternative(self):
        """Verifies chart containers have accessible labels and render accessible data alternatives."""
        self.page.evaluate('''() => {
            const chartSection = UI.chart({
                title: "Monthly Revenue Trend",
                description: "Revenue trend over past 3 months in Lakhs",
                render: () => {},
                dataTable: {
                    columns: [{ key: "month", label: "Month" }, { key: "revenue", label: "Revenue (Lakhs)" }],
                    rows: [{ month: "Jan", revenue: "45.2" }, { month: "Feb", revenue: "52.8" }]
                }
            });
            root.append(chartSection);
        }''')
        chart_section = self.page.locator('.sui-chart')
        self.assertEqual(chart_section.get_attribute('role'), 'region')
        self.assertIn("Monthly Revenue Trend", chart_section.get_attribute('aria-label'))

        canvas = self.page.locator('.sui-chart-canvas')
        self.assertEqual(canvas.get_attribute('role'), 'img')
        self.assertIn("Monthly Revenue Trend", canvas.get_attribute('aria-label'))

        # Check accessible table alternative
        alt_table = self.page.locator('.sui-chart-table-wrap table')
        self.assertEqual(alt_table.count(), 1)
        self.assertEqual(alt_table.locator('caption').text_content(), "Monthly Revenue Trend Data")
        self.assertEqual(alt_table.locator('th').all_text_contents(), ["Month", "Revenue (Lakhs)"])
        self.assertEqual(alt_table.locator('td').all_text_contents(), ["Jan", "45.2", "Feb", "52.8"])

    def test_live_announcements_for_async_updates(self):
        """Verifies frappe.sarathiUI.announce creates and updates live region."""
        self.page.evaluate('''() => {
            UI.announce("Data refresh completed successfully");
        }''')
        self.page.wait_for_timeout(100)
        announcer = self.page.locator('#sui-live-announcer')
        self.assertEqual(announcer.count(), 1)
        self.assertEqual(announcer.get_attribute('aria-live'), 'polite')
        self.assertEqual(announcer.get_attribute('aria-atomic'), 'true')
        self.assertEqual(announcer.text_content(), "Data refresh completed successfully")

    def test_prefers_reduced_motion(self):
        """Verifies animations and transitions are disabled when reduced-motion is requested."""
        reduced_page = self.browser.new_page(
            viewport={"width": 1024, "height": 768},
            reduced_motion="reduce"
        )
        try:
            reduced_page.set_content('<main data-sarathi-ui><button type="button" class="sui-action">Action</button></main>')
            reduced_page.add_style_tag(content=(PUBLIC / "css/sarathi_ui.css").read_text(encoding="utf-8"))
            btn = reduced_page.locator('.sui-action')
            anim = btn.evaluate('el => getComputedStyle(el).animationName')
            trans = btn.evaluate('el => getComputedStyle(el).transitionDuration')
            self.assertIn(anim, ("none", ""))
            self.assertIn(trans, ("0s", "0.000001s", "0.001ms"))
        finally:
            reduced_page.close()

    def test_distinguish_unavailable_vs_zero(self):
        """Verifies genuine zero is displayed as 0, while missing/failed metrics display dashes and unavailable states."""
        self.page.evaluate('''() => {
            root.append(
                UI.kpi({ label: "Valid Zero Metric", value: 0 }),
                UI.kpi({ label: "Missing Metric", value: null }),
                UI.kpi({ label: "Failed Metric", value: 5, error: true })
            );
        }''')
        values = self.page.locator('.sui-kpi-value').all_text_contents()
        self.assertEqual(values, ["0", "—", "—"])
        small_texts = self.page.locator('.sui-kpi small').all_text_contents()
        self.assertIn("Data unavailable", small_texts)


if __name__ == "__main__":
    unittest.main()
