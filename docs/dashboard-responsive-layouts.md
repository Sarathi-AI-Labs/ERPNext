# Dashboard Responsive Layouts & Breakpoints (DASH-028)

**Task ID:** DASH-028  
**Parent Epic:** DASH-027 — Responsive Design & Accessibility  
**Scope:** DASH-028 only (Responsive Breakpoints and Layouts)  
**Status:** Implemented & Verified  
**Date:** October 2026  

---

## 1. Executive Summary

As part of DASH-027 (Responsive Design & Accessibility), **DASH-028** establishes a centralized, consistent responsive layout and breakpoint system across the three core dashboard experiences of the Sarathi Industrial Control Tower:

1. **Owner & Executive Dashboard** (`sarathi_owner`, `/desk/sarathiownertower`)
2. **Production Management Control Tower** (`sarathi_visibility`, `/desk/sarathicontroltower`)
3. **Shop-Floor Supervisor & Operator Dashboard** (`sarathi_visibility`, `/desk/sarathishopfloor`)

The responsive system guarantees that all dashboards, KPI cards, analytical charts, operational tables, filter toolbars, and reporting dialogs render predictably without unexpected page-level horizontal overflow, clipped text, or squashed controls across screen sizes ranging from compact smartphones (320px) to ultra-wide desktop monitors (1440px+).

Zero changes were made to backend calculation logic, KPI formulas, ERPNext document workflows, authorization models, or Frappe core files.

---

## 2. Dashboards & Routes Inspected

| Dashboard Experience | Application | Desk Route | Primary Users | Key Layout Components |
|:---|:---|:---|:---|:---|
| **Owner & Executive Dashboard** | `sarathi_owner` | `/desk/sarathiownertower` | Business Owners, MD, CFO | Financial KPIs (8 cards), revenue charts, top customers, sales backlog table, project health, inventory summaries, executive risks & approvals. |
| **Production Control Tower** | `sarathi_visibility` | `/desk/sarathicontroltower` | Production Managers, Plant Heads | Factory overview KPIs, pipeline bottleneck view, material readiness & shortage tables, workstation downtime, quality inspections, rework, and production exceptions queue. |
| **Shop-Floor Workboard & Supervisor Overview** | `sarathi_visibility` | `/desk/sarathishopfloor` | Machine Operators, Shift Supervisors | Operator Workboard (active operation card, blocker alerts, job queue) and Supervisor Team Overview (subview switcher, 9-KPI grid, operator workload cards, live floor WIP table, completed operations table, workstation cards). |

---

## 3. Centralized Responsive Breakpoints

A standard, centralized breakpoint scale has been established in `sarathi_ui.css` using CSS custom properties on `[data-sarathi-ui]`:

```css
[data-sarathi-ui] {
  --sui-bp-sm-mobile: 320px;   /* Small Mobile (iPhone SE, Galaxy Fold outer) */
  --sui-bp-mobile:    375px;   /* Standard Mobile (iPhone 13/14/15, Pixel) */
  --sui-bp-tablet:    768px;   /* Tablet Portrait (iPad Mini, iPad Air) */
  --sui-bp-desktop:   1024px;  /* Compact Desktop / Tablet Landscape */
  --sui-bp-wide:      1440px;  /* Large Desktop Monitors (1080p, 1440p, 4K) */
}
```

### Breakpoint Matrix & Layout Behaviors

| Breakpoint Tier | Width Range (CSS px) | Layout Behavior | KPI Grids | Tables Strategy | Charts Strategy | Filter Toolbars |
|:---|:---|:---|:---|:---|:---|:---|
| **Large Desktop** | $\ge 1440\text{px}$ | Max-width expands to 1600px, centered with comfortable margins. | 4–6 columns (or auto-fill) | Full table columns with expanded whitespace | Side-by-side dual chart grid (2 columns) | Inline horizontal toolbar with flexible search |
| **Desktop** | $1024\text{px} - 1439\text{px}$ | Standard desktop layout (max-width 1400px). | 3–4 columns | Full table columns | Dual chart grid (2 columns) | Inline horizontal toolbar |
| **Tablet** | $768\text{px} - 1023\text{px}$ | Two-column dashboard layout; compact spacing (padding 16px). | 2–3 columns | Horizontally scrollable inside labeled bounded wrapper (`overflow-x: auto`) | 2 columns or stacked based on chart density | Wrapping toolbar |
| **Standard Mobile** | $375\text{px} - 767\text{px}$ | Single-column main layout; stacked sections; touch targets $\ge 44\text{px}$. | 2 columns (or 1 column if wide label) | Bounded horizontal scroll wrapper (`min-width: 620-760px`) | Stacked single column (`minmax(0, 1fr)`) | Stacked vertical controls; 100% width inputs |
| **Small Mobile** | $320\text{px} - 374\text{px}$ | Ultra-compact padding (8–10px); clamped typography; single column stacking. | 1 column (2 cols for compact 9-KPI grid with clamped labels) | Bounded horizontal scroll wrapper | Stacked single column; SVG `max-width: 100%` | Stacked vertical controls; date buttons 50/50 |

---

## 4. Key Component Strategies & Enhancements

### A. Responsive KPI Cards
- **Issue:** Fixed grid columns (`repeat(3, minmax(0, 1fr))` in `.sd-cards` and rigid card min-widths) previously caused severe horizontal squashing and text truncation on mobile devices.
- **Solution:**
  - Standardized media queries adapt `.sd-cards`, `.sd-kpis`, `.sod-finance-kpis`, and `.sf-kpi-grid`.
  - Tablet ($768 - 1023\text{px}$): 2–3 columns.
  - Mobile ($375 - 767\text{px}$): 2 columns.
  - Mobile Narrow ($< 480\text{px}$): 1 column (except compact 9-KPI grid which retains 2 columns with clamped labels).
  - Small Mobile ($320 - 374\text{px}$): Font size clamped (`clamp(1.2rem, 5.5vw, 1.8rem)`), padding reduced to `10px 8px`, removing `white-space: nowrap !important` constraints on mobile so labels wrap naturally without clipping.

### B. Responsive Tables Strategy
- **Issue:** Wide 8-to-10 column operational tables (Work Orders, Job Cards, Material Deficits, Quality Inspections, Production Exceptions, Floor Active WIP, and Customer Sales Backlog) forced the entire dashboard page body to expand horizontally on mobile screens.
- **Solution:**
  - Universal bounded container rule applied across all table wrappers:
    ```css
    [data-sarathi-ui] :is(.sui-table-region, .sd-table-wrap, .sd-table-container, .sf-table-card, .sod-tablewrap, .sd-exceptions-table-container) {
      max-width: 100%;
      min-width: 0;
      overflow-x: auto;
      overscroll-behavior-x: contain;
      -webkit-overflow-scrolling: touch;
    }
    ```
  - Tables inside wrappers maintain a sensible minimum width (`min-width: 580px - 760px`) so individual column headers and data points remain readable without vertical squashing.
  - Horizontal scrolling is strictly contained within the table card, completely preventing the outer window/body from scrolling horizontally.

### C. Responsive Charts & Analytics
- **Issue:** Dual-column `.sd-chart-grid` in Control Tower was rendered side-by-side on mobile screens, squashing donut and bar charts down to unusable widths.
- **Solution:**
  - Applied `.sd-chart-grid { grid-template-columns: minmax(0, 1fr); }` on screens $\le 767\text{px}$.
  - Chart SVGs and canvases constrained with `min-width: 0; max-width: 100%; height: auto;`.
  - Chart legends wrap cleanly with touch-friendly spacing.

### D. Filter Bars, Controls & Navigation
- **Issue:** Inline filter groups and date picker submit/reset button pairs clipped or overflowed when viewport width was narrower than the accumulated flex width.
- **Solution:**
  - On screens $\le 767\text{px}$, filter toolbars switch to column stacking:
    `.sd-controls label, .sui-filters label, .sf-filter-group { flex: 1 1 100%; width: 100%; min-width: 0; }`
  - Input, select, and search elements expand to 100% width with touch-friendly height (`min-height: 44px; font-size: 16px;`), which also prevents unwanted iOS auto-zoom on form focus.
  - Date action button groups (`.sd-date-btn-group`) span 100% width with equal flex distribution.

### E. Responsive Dialogs & Modals
- **Issue:** Native desktop dialogs could exceed mobile viewport boundaries or push action buttons below the bottom of the screen.
- **Solution:**
  - Universal modal dialog constraints established:
    ```css
    :is(.modal-dialog, [data-sarathi-ui] .modal-dialog) {
      max-width: min(94vw, 640px) !important;
      margin: 16px auto !important;
    }
    :is(.modal-content, [data-sarathi-ui] .modal-content) {
      max-height: calc(100vh - 32px);
      display: flex;
      flex-direction: column;
    }
    :is(.modal-body, [data-sarathi-ui] .modal-body) {
      overflow-y: auto;
      -webkit-overflow-scrolling: touch;
    }
    ```
  - Small Mobile ($320 - 374\text{px}$): Dialog margins tighten to `8px` (`max-width: calc(100vw - 16px)`), keeping header, body, and action buttons accessible.

### F. Mobile-First Shop-Floor Improvements
- **Subview Switcher:** Tab container uses `flex-wrap: wrap;`. On mobile, tabs share width equally (`flex: 1 1 calc(50% - 6px); min-height: 44px;`). On small mobile ($< 375\text{px}$), tabs stack vertically.
- **Supervisor 9 KPIs Grid:** Uses auto-fill grid that scales from 5 cols (desktop) $\rightarrow$ 3 cols (mobile) $\rightarrow$ 2 cols (small mobile). Subtitle labels are hidden on $< 375\text{px}$ to preserve numeral prominence.
- **Operator Workload Cards:** Replaced rigid `minmax(320px, 1fr)` with `minmax(0, 1fr)` on mobile so cards fit 320px screens without clipping.
- **Touch Targets:** All primary reporting buttons (`Start Job`, `Report Progress`, `Pause`, `Resume`, `Stop`, `Complete`) enforce minimum 44px touch height with wrapping action rows.

---

## 5. Viewport Verification Matrix

All three dashboards and responsive dialogs were tested using automated Playwright tests in `sarathi_visibility/tests/test_responsive_layouts.py` across the 7 representative viewports:

| Viewport Dimension | Target Device Category | Page-Level Horizontal Scroll? | KPI Cards Layout | Table Container Behavior | Filter Bar Behavior | Dialog Viewport Fit | Result |
|:---|:---|:---|:---|:---|:---|:---|:---|
| **320 × 640** | Small Mobile (iPhone SE, Galaxy Fold) | **No** (`scrollWidth <= 320px`) | 1–2 columns, clamped font | Bounded horizontal scroll | Stacked 100% width | Fits within viewport | **PASS** |
| **375 × 812** | Standard Mobile (iPhone 13/14/15) | **No** (`scrollWidth <= 375px`) | 2 columns | Bounded horizontal scroll | Stacked 100% width | Fits within viewport | **PASS** |
| **430 × 932** | Large Mobile (iPhone Pro Max, Pixel XL) | **No** (`scrollWidth <= 430px`) | 2 columns | Bounded horizontal scroll | Stacked 100% width | Fits within viewport | **PASS** |
| **768 × 1024** | Tablet Portrait (iPad 10th gen, Mini) | **No** (`scrollWidth <= 768px`) | 2–3 columns | Bounded horizontal scroll | Wrapping inline controls | Centered modal | **PASS** |
| **1024 × 768** | Tablet Landscape / Compact Laptop | **No** (`scrollWidth <= 1024px`) | 3–4 columns | Full columns with scroll fallback | Inline controls | Centered modal | **PASS** |
| **1366 × 768** | Standard Laptop Screen | **No** (`scrollWidth <= 1366px`) | 4 columns | Full table visible | Inline controls | Centered modal | **PASS** |
| **1440 × 900** | Large Desktop Monitor | **No** (`scrollWidth <= 1440px`) | 4–6 columns | Full table visible (max 1600px) | Inline controls | Centered modal | **PASS** |

---

## 6. Test Execution Results

```text
======================================================================
1. Automated Responsive Viewport Tests (test_responsive_layouts.py):
----------------------------------------------------------------------
test_owner_dashboard_responsive ...................................... PASS
test_production_control_tower_responsive ............................. PASS
test_responsive_dialogs_fit_viewports ................................ PASS
test_shopfloor_operator_workboard_responsive ......................... PASS
test_shopfloor_supervisor_overview_responsive ........................ PASS
Ran 5 tests (35 viewport subtests) in 4.280s -> OK

======================================================================
2. Shared Presentation Contract Tests (test_shared_ui_browser.py):
----------------------------------------------------------------------
Ran 12 tests in 4.442s -> OK (100% passing)

======================================================================
3. Backend Logic & Calculation Regressions:
----------------------------------------------------------------------
test_shopfloor_logic.py .............................................. 29/29 PASS (0.023s)
test_production_exceptions_logic.py .................................. 10/10 PASS (0.008s)
======================================================================
```

---

## 7. Modified Files

| File | Purpose | Scope of Changes |
|:---|:---|:---|
| `sarathi_visibility/sarathi_visibility/public/css/sarathi_ui.css` | Shared UI Token & Design System | Added centralized breakpoint custom properties (`--sui-bp-*`), universal table container scroll rules, table readability safeguard (`min-width: 580px`), responsive chart constraints, dialog bounding rules, and unified media queries for 320px, 375px, 768px, 1024px, and 1440px+. |
| `sarathi_visibility/sarathi_visibility/public/css/sarathi_shopfloor.css` | Shop-Floor & Supervisor Styles | Made `.sf-table-card` scrollable with `min-width: 720px` on `.sf-data-table`, added `flex-wrap` and 44px min-height to subview switcher, and added comprehensive mobile/tablet media queries for supervisor toolbar, 9-KPI cards, workload cards, and touch action buttons. |
| `sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css` | Production Control Tower Styles | Added bounded scroll styling to `.sd-table-wrap`, `.sd-table-container`, and `.sd-exceptions-table-container`, and added comprehensive DASH-028 media queries covering hero stacking, control stacking, 2-to-1 column KPI cards, single-column charts, and small-mobile padding. |
| `sarathi_owner/sarathi_owner/public/css/sarathi_owner_homepage.css` | Owner Homepage Styles | Added large desktop container boundaries (1600px) and small mobile ($320 - 374\text{px}$) padding/font optimizations for financial KPIs and filter sections. |
| `sarathi_visibility/sarathi_visibility/tests/test_responsive_layouts.py` | Automated Responsive Tests | New Playwright test suite verifying zero horizontal overflow, KPI grid adaptability, touch targets, and modal viewport fits across all 7 standard viewports. |
| `docs/dashboard-responsive-layouts.md` | Feature Documentation | This document. |

---

## 8. Strict Scope Control & DASH-029 Confirmation

- **DASH-028 only** was implemented in this execution.
- **DASH-029** (Accessibility & Status Conventions) was **NOT** automatically implemented and is queued pending explicit user instruction.
- Zero modifications were made to ERPNext core files, backend calculations, KPI formulas, or authorization logic.
