"""
Script to build clean single-column sarathi_dashboard.css
Without any sidebar, with vibrant colors, elegant typography, and well-formatted cards.
"""

# Read base CSS up to line 4536
with open("scratch/sarathi_dashboard_88b00db.css", encoding="utf-8") as f:
    lines = f.readlines()

base_css = "".join(lines[:4536])

dashboard_theme_css = """

/* ==========================================================================
   SARATHI CONTROL TOWER · ULTRA-PREMIUM SINGLE-COLUMN INDUSTRIAL THEME
   No sidebar. Clean, radiant layout with rich color combinations,
   modern typography, distinct card borders, 3D hover lifts, and zero cutoffs.
   ========================================================================== */

/* 1. Typography Imports */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700;800&family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

/* 2. Global Resets for Frappe Page Wrapper (Zero Sidebar, Full Width Single Column) */
.page-container[data-page-route="sarathicontroltower"],
.page-container[data-page-route="sarathicontroltower"] .page-body,
.page-container[data-page-route="sarathicontroltower"] .page-wrapper,
.page-container[data-page-route="sarathicontroltower"] .page-content,
.page-container[data-page-route="sarathicontroltower"] .layout-main,
.page-container[data-page-route="sarathicontroltower"] .layout-main-section-wrapper,
.page-container[data-page-route="sarathicontroltower"] .layout-main-section {
  padding: 0 !important;
  margin: 0 !important;
  max-width: 100% !important;
  width: 100% !important;
  box-sizing: border-box !important;
  background: #f8fafc !important;
}

[data-page-route="sarathicontroltower"] .page-head {
  display: none !important;
}

/* 3. Master Dashboard Canvas */
.sd-dashboard {
  --sd-font-sans: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --sd-font-head: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
  --sd-font-mono: 'JetBrains Mono', 'SF Mono', Consolas, monospace;

  --sd-primary: #2563eb;
  --sd-indigo: #4f46e5;
  --sd-cyan: #0284c7;
  --sd-teal: #0d9488;
  --sd-emerald: #059669;
  --sd-amber: #d97706;
  --sd-rose: #e11d48;
  --sd-purple: #7c3aed;

  --sd-bg: #f8fafc;
  --sd-card-bg: #ffffff;
  --sd-border: #e2e8f0;
  --sd-border-hover: #cbd5e1;
  --sd-ink: #0f172a;
  --sd-ink-sub: #334155;
  --sd-muted: #64748b;

  font-family: var(--sd-font-sans) !important;
  color: var(--sd-ink) !important;
  background-color: #f8fafc !important;
  background-image:
    radial-gradient(ellipse at 10% 5%, rgba(37, 99, 235, 0.04) 0%, transparent 45%),
    radial-gradient(ellipse at 90% 15%, rgba(13, 148, 136, 0.04) 0%, transparent 45%),
    radial-gradient(ellipse at 50% 90%, rgba(124, 58, 237, 0.03) 0%, transparent 50%) !important;
  min-height: 100vh !important;
  padding: 0 32px 48px 32px !important;
  box-sizing: border-box !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 22px !important;
  width: 100% !important;
  max-width: 1720px !important;
  margin: 0 auto !important;
}

.sd-dashboard * {
  box-sizing: border-box !important;
}

/* 4. Top View Switcher Bar (Owner Executive View ⇄ Production Operations View) */
.sd-switcher-bar {
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  background: #090e17 !important;
  padding: 10px 24px !important;
  margin: 0 -32px 10px -32px !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: #cbd5e1 !important;
  box-sizing: border-box !important;
  width: calc(100% + 64px) !important;
}

.sd-switcher-label {
  font-size: 11px !important;
  font-weight: 850 !important;
  text-transform: uppercase !important;
  letter-spacing: 1.5px !important;
  color: #64748b !important;
}

.sd-switcher-btn {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  background: rgba(255, 255, 255, 0.07) !important;
  border: 1px solid rgba(255, 255, 255, 0.14) !important;
  color: #cbd5e1 !important;
  padding: 6px 16px !important;
  border-radius: 12px !important;
  font-size: 12px !important;
  font-weight: 750 !important;
  cursor: pointer !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.sd-switcher-btn:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #ffffff !important;
  transform: translateY(-1px) !important;
}

.sd-switcher-btn.active {
  background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%) !important;
  border-color: transparent !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
}

.sd-switcher-icon {
  font-size: 14px !important;
}

/* 5. Hero Header Section */
.sd-dashboard .sd-hero {
  background: linear-gradient(135deg, #091a30 0%, #172554 50%, #064e3b 100%) !important;
  border-radius: 20px !important;
  padding: 32px 36px !important;
  box-shadow: 0 16px 36px -10px rgba(9, 26, 48, 0.35) !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  position: relative !important;
  overflow: hidden !important;
  isolation: isolate !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.sd-dashboard .sd-hero::before {
  content: "" !important;
  position: absolute !important;
  top: -60% !important;
  right: -10% !important;
  width: 500px !important;
  height: 500px !important;
  border-radius: 50% !important;
  background: radial-gradient(circle, rgba(56, 189, 248, 0.18) 0%, transparent 70%) !important;
  pointer-events: none !important;
  z-index: -1 !important;
}

.sd-dashboard .sd-hero::after {
  content: "" !important;
  position: absolute !important;
  bottom: -40% !important;
  left: 20% !important;
  width: 400px !important;
  height: 400px !important;
  border-radius: 50% !important;
  background: radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, transparent 70%) !important;
  pointer-events: none !important;
  z-index: -1 !important;
}

.sd-dashboard .sd-eyebrow {
  font-size: 11.5px !important;
  font-weight: 850 !important;
  text-transform: uppercase !important;
  letter-spacing: 2.2px !important;
  color: #38bdf8 !important;
  margin-bottom: 6px !important;
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
}

.sd-dashboard .sd-eyebrow::before {
  content: "✦" !important;
  font-size: 13px !important;
  color: #38bdf8 !important;
}

.sd-dashboard .sd-hero h1 {
  font-family: var(--sd-font-head) !important;
  font-size: clamp(26px, 2.5vw, 36px) !important;
  font-weight: 850 !important;
  letter-spacing: -0.6px !important;
  color: #ffffff !important;
  margin: 0 0 6px 0 !important;
}

.sd-dashboard .sd-hero p {
  font-size: 14.5px !important;
  color: #cbd5e1 !important;
  margin: 0 !important;
  font-weight: 500 !important;
}

.sd-dashboard .sd-hero-actions {
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  flex-shrink: 0 !important;
}

.sd-dashboard [data-updated] {
  font-size: 12px !important;
  font-weight: 650 !important;
  color: #a7f3d0 !important;
  background: rgba(6, 78, 59, 0.6) !important;
  border: 1px solid rgba(16, 185, 129, 0.35) !important;
  border-radius: 20px !important;
  padding: 6px 14px !important;
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
}

.sd-dashboard [data-updated]::before {
  content: "" !important;
  width: 7px !important;
  height: 7px !important;
  border-radius: 50% !important;
  background: #34d399 !important;
  box-shadow: 0 0 8px #34d399 !important;
}

.sd-dashboard .sd-hero .sd-button {
  background: rgba(255, 255, 255, 0.12) !important;
  border: 1px solid rgba(255, 255, 255, 0.22) !important;
  color: #ffffff !important;
  border-radius: 12px !important;
  padding: 9px 18px !important;
  font-size: 13px !important;
  font-weight: 750 !important;
  cursor: pointer !important;
  backdrop-filter: blur(8px) !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.sd-dashboard .sd-hero .sd-button:hover {
  background: rgba(255, 255, 255, 0.25) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25) !important;
}

.sd-dashboard .sd-hero .sd-ai-header-btn {
  background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.3) !important;
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.4) !important;
}

.sd-dashboard .sd-hero .sd-ai-header-btn:hover {
  background: linear-gradient(135deg, #6d28d9 0%, #9333ea 100%) !important;
  box-shadow: 0 6px 22px rgba(124, 58, 237, 0.6) !important;
}

/* 6. Filter Controls Toolbar (Perfect Align, High Contrast, No Detached Floating Text) */
.sd-dashboard .sd-controls {
  display: flex !important;
  flex-wrap: wrap !important;
  align-items: flex-end !important;
  gap: 16px !important;
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 18px !important;
  padding: 20px 24px !important;
  box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.05) !important;
}

.sd-dashboard .sd-controls label {
  display: flex !important;
  flex-direction: column !important;
  gap: 6px !important;
  font-size: 11px !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.8px !important;
  color: #334155 !important;
  margin: 0 !important;
  position: static !important;
}

.sd-dashboard .sd-controls label::before,
.sd-dashboard .sd-controls label::after {
  display: none !important;
}

.sd-dashboard .sd-controls select,
.sd-dashboard .sd-controls input {
  height: 42px !important;
  min-width: 175px !important;
  border: 1.5px solid #cbd5e1 !important;
  border-radius: 10px !important;
  background: #f8fafc !important;
  color: #0f172a !important;
  font-size: 13.5px !important;
  font-weight: 600 !important;
  padding: 8px 12px !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.sd-dashboard .sd-controls select:focus,
.sd-dashboard .sd-controls input:focus {
  border-color: #0284c7 !important;
  background: #ffffff !important;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.15) !important;
  outline: none !important;
}

.sd-dashboard .sd-date-btn-group {
  display: flex !important;
  gap: 8px !important;
  align-items: flex-end !important;
}

.sd-dashboard .sd-controls .sd-button {
  height: 42px !important;
  padding: 0 20px !important;
  border-radius: 10px !important;
  font-size: 13px !important;
  font-weight: 750 !important;
  cursor: pointer !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  border: 1.5px solid #cbd5e1 !important;
  background: #f8fafc !important;
  color: #334155 !important;
}

.sd-dashboard .sd-controls .sd-button:hover {
  background: #e2e8f0 !important;
  transform: translateY(-1px) !important;
}

.sd-dashboard .sd-controls .sd-button.sd-primary {
  background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
  border-color: transparent !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
}

.sd-dashboard .sd-controls .sd-button.sd-primary:hover {
  background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%) !important;
  box-shadow: 0 6px 18px rgba(2, 132, 199, 0.5) !important;
}

.sd-dashboard .sd-controls .sd-search {
  flex: 1 1 280px !important;
}

.sd-dashboard .sd-controls .sd-search input {
  width: 100% !important;
}

/* 7. Scope Note & Breadcrumb */
.sd-dashboard .sd-scope-note {
  font-size: 12.5px !important;
  color: #64748b !important;
  background: #f1f5f9 !important;
  border-left: 3.5px solid #0284c7 !important;
  padding: 10px 16px !important;
  border-radius: 0 10px 10px 0 !important;
  margin: 0 !important;
  line-height: 1.5 !important;
}

.sd-dashboard .sd-breadcrumb {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  font-size: 13px !important;
  font-weight: 650 !important;
  color: #475569 !important;
}

.sd-dashboard .sd-breadcrumb a {
  color: #0284c7 !important;
  text-decoration: none !important;
}

.sd-dashboard .sd-breadcrumb a:hover {
  text-decoration: underline !important;
}

/* 8. Radiant Summary KPI Cards (6 Distinct Gem Themes, 3D Elevation) */
.sd-dashboard .sd-kpis {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)) !important;
  gap: 16px !important;
  width: 100% !important;
}

.sd-dashboard .sd-kpi {
  --kpi-theme: #4f46e5;
  --kpi-bg: #eef2ff;
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-top: 4px solid var(--kpi-theme) !important;
  border-radius: 16px !important;
  padding: 20px !important;
  min-height: 130px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
  box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04) !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  cursor: pointer !important;
  text-align: left !important;
}

.sd-dashboard .sd-kpi:hover {
  transform: translateY(-4px) !important;
  border-color: #cbd5e1 !important;
  box-shadow: 0 16px 32px -6px rgba(15, 23, 42, 0.1) !important;
}

/* KPI 6-Tone Gem Color Schemes */
.sd-dashboard .sd-kpi.sd-tone-0,
.sd-dashboard .sd-kpi:nth-child(6n+1) {
  --kpi-theme: #4f46e5;
  --kpi-bg: #eef2ff;
  border-top-color: #4f46e5 !important;
  background: linear-gradient(135deg, #ffffff 65%, #eef2ff 100%) !important;
}

.sd-dashboard .sd-kpi.sd-tone-1,
.sd-dashboard .sd-kpi:nth-child(6n+2) {
  --kpi-theme: #059669;
  --kpi-bg: #ecfdf5;
  border-top-color: #059669 !important;
  background: linear-gradient(135deg, #ffffff 65%, #ecfdf5 100%) !important;
}

.sd-dashboard .sd-kpi.sd-tone-2,
.sd-dashboard .sd-kpi:nth-child(6n+3) {
  --kpi-theme: #d97706;
  --kpi-bg: #fffbeb;
  border-top-color: #d97706 !important;
  background: linear-gradient(135deg, #ffffff 65%, #fffbeb 100%) !important;
}

.sd-dashboard .sd-kpi.sd-tone-3,
.sd-dashboard .sd-kpi:nth-child(6n+4) {
  --kpi-theme: #7c3aed;
  --kpi-bg: #f5f3ff;
  border-top-color: #7c3aed !important;
  background: linear-gradient(135deg, #ffffff 65%, #f5f3ff 100%) !important;
}

.sd-dashboard .sd-kpi.sd-tone-4,
.sd-dashboard .sd-kpi:nth-child(6n+5) {
  --kpi-theme: #e11d48;
  --kpi-bg: #fff1f2;
  border-top-color: #e11d48 !important;
  background: linear-gradient(135deg, #ffffff 65%, #fff1f2 100%) !important;
}

.sd-dashboard .sd-kpi.sd-tone-5,
.sd-dashboard .sd-kpi:nth-child(6n+6) {
  --kpi-theme: #0284c7;
  --kpi-bg: #f0f9ff;
  border-top-color: #0284c7 !important;
  background: linear-gradient(135deg, #ffffff 65%, #f0f9ff 100%) !important;
}

.sd-dashboard .sd-metric-label {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
  font-size: 12px !important;
  font-weight: 750 !important;
  color: #475569 !important;
  text-transform: capitalize !important;
}

.sd-dashboard .sd-metric-label .sarathi-ui-icon {
  color: var(--kpi-theme) !important;
  background: var(--kpi-bg) !important;
  padding: 6px !important;
  border-radius: 8px !important;
  box-sizing: content-box !important;
  width: 18px !important;
  height: 18px !important;
}

.sd-dashboard .sd-kpi strong {
  font-family: var(--sd-font-mono) !important;
  font-size: 28px !important;
  font-weight: 850 !important;
  color: var(--kpi-theme) !important;
  letter-spacing: -0.8px !important;
  line-height: 1.1 !important;
  margin: 8px 0 4px 0 !important;
}

.sd-dashboard .sd-kpi small {
  font-size: 11.5px !important;
  color: #64748b !important;
  font-weight: 550 !important;
}

/* 9. Panels & Panel Headings */
.sd-dashboard .sd-panel {
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 20px !important;
  padding: 26px !important;
  box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.04) !important;
  width: 100% !important;
  margin-bottom: 22px !important;
}

.sd-dashboard .sd-panel-heading {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  padding-bottom: 16px !important;
  border-bottom: 1.5px solid #f1f5f9 !important;
  margin-bottom: 22px !important;
  gap: 16px !important;
}

.sd-dashboard .sd-panel-heading h2 {
  font-family: var(--sd-font-head) !important;
  font-size: 20px !important;
  font-weight: 800 !important;
  letter-spacing: -0.4px !important;
  color: #0f172a !important;
  margin: 0 0 4px 0 !important;
}

.sd-dashboard .sd-panel-heading p {
  font-size: 13px !important;
  color: #64748b !important;
  margin: 0 !important;
  font-weight: 500 !important;
}

.sd-dashboard .sd-panel-heading .sd-button {
  background: #f8fafc !important;
  border: 1.5px solid #cbd5e1 !important;
  border-radius: 10px !important;
  padding: 8px 16px !important;
  font-size: 12.5px !important;
  font-weight: 750 !important;
  color: #334155 !important;
  cursor: pointer !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.sd-dashboard .sd-panel-heading .sd-button:hover {
  background: #e2e8f0 !important;
  color: #0f172a !important;
  transform: translateY(-1px) !important;
}

/* 10. Multi-Card Grid Containers (Customers, Projects) */
.sd-dashboard .sd-cards {
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(285px, 1fr)) !important;
  gap: 18px !important;
  width: 100% !important;
}

/* Customer & Project Cards */
.sd-dashboard .sd-card {
  --card-accent: #2563eb;
  --card-light: #eff6ff;
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-top: 4.5px solid var(--card-accent) !important;
  border-radius: 16px !important;
  padding: 22px !important;
  display: flex !important;
  flex-direction: column !important;
  justify-content: space-between !important;
  min-height: 155px !important;
  text-align: left !important;
  cursor: pointer !important;
  position: relative !important;
  overflow: hidden !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03) !important;
}

.sd-dashboard .sd-card:hover {
  transform: translateY(-4px) !important;
  border-color: #cbd5e1 !important;
  border-top-color: var(--card-accent) !important;
  box-shadow: 0 16px 32px -8px rgba(15, 23, 42, 0.12) !important;
}

/* 6 Alternating Gem Accent Themes for Customer & Project Cards */
.sd-dashboard .sd-card:nth-child(6n+1) {
  --card-accent: #2563eb;
  --card-light: #eff6ff;
  background: linear-gradient(180deg, #f8faff 0%, #ffffff 40%) !important;
}

.sd-dashboard .sd-card:nth-child(6n+2) {
  --card-accent: #059669;
  --card-light: #ecfdf5;
  background: linear-gradient(180deg, #f0fdf4 0%, #ffffff 40%) !important;
}

.sd-dashboard .sd-card:nth-child(6n+3) {
  --card-accent: #d97706;
  --card-light: #fffbeb;
  background: linear-gradient(180deg, #fffbeb 0%, #ffffff 40%) !important;
}

.sd-dashboard .sd-card:nth-child(6n+4) {
  --card-accent: #7c3aed;
  --card-light: #f5f3ff;
  background: linear-gradient(180deg, #faf5ff 0%, #ffffff 40%) !important;
}

.sd-dashboard .sd-card:nth-child(6n+5) {
  --card-accent: #e11d48;
  --card-light: #fff1f2;
  background: linear-gradient(180deg, #fff1f2 0%, #ffffff 40%) !important;
}

.sd-dashboard .sd-card:nth-child(6n+6) {
  --card-accent: #0284c7;
  --card-light: #f0f9ff;
  background: linear-gradient(180deg, #f0f9ff 0%, #ffffff 40%) !important;
}

.sd-dashboard .sd-card h3 {
  font-family: var(--sd-font-head) !important;
  font-size: 16.5px !important;
  font-weight: 750 !important;
  color: #0f172a !important;
  margin: 0 0 6px 0 !important;
  line-height: 1.35 !important;
}

.sd-dashboard .sd-card p {
  font-size: 13px !important;
  color: #64748b !important;
  margin: 0 0 10px 0 !important;
  line-height: 1.5 !important;
}

.sd-dashboard .sd-card small {
  font-size: 11.5px !important;
  font-weight: 700 !important;
  color: var(--card-accent) !important;
  margin-top: 8px !important;
  display: inline-block !important;
}

/* 11. SINGLE-CARD PANELS: Subcontracting & Finance/Accounting (CRITICAL FIX) */
/* Override .sd-cards grid for panels that contain only ONE large executive card! */
.sd-dashboard [data-subcontracting-cards],
.sd-dashboard [data-accounting-cards] {
  display: block !important;
  width: 100% !important;
}

/* A. Subcontracting Operations Main Card */
.sd-dashboard .sd-subcontracting-main-card {
  width: 100% !important;
  max-width: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  background: linear-gradient(135deg, #ffffff 70%, #f0fdf4 100%) !important;
  border: 1.5px solid #bbf7d0 !important;
  border-top: 4.5px solid #059669 !important;
  border-radius: 18px !important;
  padding: 24px 28px !important;
  box-shadow: 0 6px 20px rgba(5, 150, 105, 0.06) !important;
  cursor: pointer !important;
  text-align: left !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.sd-dashboard .sd-subcontracting-main-card:hover {
  transform: translateY(-3px) !important;
  box-shadow: 0 16px 36px -6px rgba(5, 150, 105, 0.16) !important;
  border-color: #86efac !important;
}

.sd-dashboard .sd-subcontracting-main-card h3 {
  font-family: var(--sd-font-head) !important;
  font-size: 19px !important;
  font-weight: 800 !important;
  color: #064e3b !important;
  margin: 6px 0 10px 0 !important;
}

.sd-dashboard .sd-subcontracting-main-card p {
  font-size: 13.5px !important;
  color: #334155 !important;
  margin: 4px 0 !important;
}

.sd-dashboard .sd-subcontracting-main-card p b {
  font-family: var(--sd-font-mono) !important;
  font-weight: 750 !important;
  color: #0f172a !important;
}

.sd-dashboard .sd-sub-card-mat b {
  color: #059669 !important;
  font-size: 15px !important;
}

/* B. Finance & Accounting Main Card (NO CUTTING, FULL WIDTH, ELEGANT 6 CHIPS) */
.sd-dashboard .sd-accounting-main-card {
  width: 100% !important;
  max-width: 100% !important;
  display: flex !important;
  flex-direction: column !important;
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-top: 4.5px solid #4f46e5 !important;
  border-radius: 18px !important;
  padding: 24px 28px !important;
  box-shadow: 0 6px 22px rgba(79, 70, 229, 0.06) !important;
  cursor: pointer !important;
  text-align: left !important;
  position: relative !important;
  overflow: hidden !important;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.sd-dashboard .sd-accounting-main-card:hover {
  transform: translateY(-3px) !important;
  box-shadow: 0 16px 36px -6px rgba(79, 70, 229, 0.16) !important;
  border-color: #cbd5e1 !important;
}

.sd-dashboard .sd-acc-card-top-strip {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  height: 4.5px !important;
  background: linear-gradient(90deg, #4f46e5 0%, #06b6d4 50%, #10b981 100%) !important;
}

.sd-dashboard .sd-acc-card-header {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  gap: 16px !important;
  width: 100% !important;
  margin-bottom: 16px !important;
}

.sd-dashboard .sd-acc-card-title-wrap {
  display: flex !important;
  align-items: center !important;
  gap: 14px !important;
}

.sd-dashboard .sd-acc-card-icon {
  width: 44px !important;
  height: 44px !important;
  border-radius: 12px !important;
  background: #eef2ff !important;
  color: #4f46e5 !important;
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  flex-shrink: 0 !important;
}

.sd-dashboard .sd-acc-card-icon svg {
  width: 22px !important;
  height: 22px !important;
}

.sd-dashboard .sd-acc-card-tag {
  font-size: 11px !important;
  font-weight: 850 !important;
  letter-spacing: 1.2px !important;
  text-transform: uppercase !important;
  color: #4f46e5 !important;
}

.sd-dashboard .sd-acc-card-header h3 {
  font-family: var(--sd-font-head) !important;
  font-size: 21px !important;
  font-weight: 850 !important;
  color: #0f172a !important;
  margin: 2px 0 0 0 !important;
  white-space: nowrap !important;
  letter-spacing: -0.4px !important;
}

.sd-dashboard .sd-acc-card-header .sd-pill {
  font-family: var(--sd-font-mono) !important;
  font-size: 13px !important;
  font-weight: 800 !important;
  padding: 6px 16px !important;
  border-radius: 20px !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
}

.sd-dashboard .sd-acc-card-main-val {
  display: flex !important;
  align-items: baseline !important;
  gap: 14px !important;
  margin-bottom: 20px !important;
  padding-bottom: 16px !important;
  border-bottom: 1.5px solid #f1f5f9 !important;
}

.sd-dashboard .sd-acc-card-main-val small {
  font-size: 12.5px !important;
  font-weight: 700 !important;
  color: #64748b !important;
  text-transform: uppercase !important;
  letter-spacing: 0.6px !important;
}

.sd-dashboard .sd-acc-card-main-val strong {
  font-family: var(--sd-font-mono) !important;
  font-size: 32px !important;
  font-weight: 850 !important;
  letter-spacing: -1px !important;
}

.sd-dashboard .sd-acc-card-main-val strong.sd-acc-positive {
  color: #059669 !important;
}

.sd-dashboard .sd-acc-card-main-val strong.sd-acc-negative {
  color: #e11d48 !important;
}

/* 6-Column Stat Chips Grid */
.sd-dashboard .sd-acc-card-chips {
  display: grid !important;
  grid-template-columns: repeat(6, 1fr) !important;
  gap: 12px !important;
  width: 100% !important;
}

.sd-dashboard .sd-acc-chip {
  border-radius: 12px !important;
  padding: 12px 14px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 4px !important;
  border: 1.5px solid transparent !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.sd-dashboard .sd-acc-chip:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 16px -2px rgba(15, 23, 42, 0.08) !important;
}

.sd-dashboard .sd-acc-chip span {
  font-size: 11px !important;
  font-weight: 750 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
}

.sd-dashboard .sd-acc-chip b {
  font-family: var(--sd-font-mono) !important;
  font-size: 16px !important;
  font-weight: 800 !important;
  letter-spacing: -0.4px !important;
}

.sd-dashboard .sd-acc-chip-blue {
  background: #eff6ff !important;
  border-color: #bfdbfe !important;
  color: #1d4ed8 !important;
}

.sd-dashboard .sd-acc-chip-rose {
  background: #fff1f2 !important;
  border-color: #fecdd3 !important;
  color: #be123c !important;
}

.sd-dashboard .sd-acc-chip-amber {
  background: #fffbeb !important;
  border-color: #fde68a !important;
  color: #b45309 !important;
}

.sd-dashboard .sd-acc-chip-crimson {
  background: #fef2f2 !important;
  border-color: #fecaca !important;
  color: #b91c1c !important;
}

.sd-dashboard .sd-acc-chip-teal {
  background: #f0fdf4 !important;
  border-color: #bbf7d0 !important;
  color: #15803d !important;
}

.sd-dashboard .sd-acc-chip-purple {
  background: #f5f3ff !important;
  border-color: #ddd6fe !important;
  color: #6d28d9 !important;
}

/* 12. Analysis Horizontal Tabs Navigation */
.sd-dashboard .sd-tabs {
  background: #0f172a !important;
  padding: 8px !important;
  border-radius: 16px !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 6px !important;
  box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.15) !important;
  margin-top: 10px !important;
}

.sd-dashboard .sd-tabs button {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  background: transparent !important;
  color: #94a3b8 !important;
  border: 1px solid transparent !important;
  border-radius: 10px !important;
  padding: 10px 16px !important;
  font-size: 13px !important;
  font-weight: 650 !important;
  cursor: pointer !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.sd-dashboard .sd-tabs button:hover {
  color: #ffffff !important;
  background: rgba(255, 255, 255, 0.08) !important;
}

.sd-dashboard .sd-tabs button.active {
  background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
  color: #ffffff !important;
  font-weight: 750 !important;
  border-color: transparent !important;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
}

/* 13. Data Tables & Status Pills */
.sd-dashboard .sd-table-wrap {
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 14px !important;
  overflow: hidden !important;
  background: #ffffff !important;
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.03) !important;
  width: 100% !important;
  margin-top: 16px !important;
}

.sd-dashboard .sd-table {
  width: 100% !important;
  border-collapse: collapse !important;
  text-align: left !important;
}

.sd-dashboard .sd-table th {
  background: #f8fafc !important;
  color: #475569 !important;
  font-size: 11.5px !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.8px !important;
  padding: 14px 16px !important;
  border-bottom: 2px solid #e2e8f0 !important;
}

.sd-dashboard .sd-table td {
  padding: 13px 16px !important;
  border-bottom: 1px solid #f1f5f9 !important;
  font-size: 13px !important;
  color: #1e293b !important;
  font-variant-numeric: tabular-nums !important;
}

.sd-dashboard .sd-table tbody tr:nth-child(even) {
  background: #fbfcfe !important;
}

.sd-dashboard .sd-table tbody tr:hover {
  background: #f0f7ff !important;
}

/* Status Pills */
.sd-dashboard .sd-pill {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  padding: 4px 12px !important;
  border-radius: 20px !important;
  font-size: 11.5px !important;
  font-weight: 750 !important;
  line-height: 1.3 !important;
}

.sd-dashboard .sd-status-green {
  background: #ecfdf5 !important;
  color: #047857 !important;
  border: 1px solid #a7f3d0 !important;
}

.sd-dashboard .sd-status-blue {
  background: #eff6ff !important;
  color: #1d4ed8 !important;
  border: 1px solid #bfdbfe !important;
}

.sd-dashboard .sd-status-amber {
  background: #fffbeb !important;
  color: #b45309 !important;
  border: 1px solid #fde68a !important;
}

.sd-dashboard .sd-status-red {
  background: #fef2f2 !important;
  color: #b91c1c !important;
  border: 1px solid #fecaca !important;
}

.sd-dashboard .sd-status-purple {
  background: #f5f3ff !important;
  color: #6d28d9 !important;
  border: 1px solid #ddd6fe !important;
}

/* 14. Detail Views & Inner Sections */
.sd-dashboard [data-subcontracting-view],
.sd-dashboard [data-accounting-view],
.sd-dashboard [data-content] {
  width: 100% !important;
}

.sd-dashboard .sd-sub-header {
  padding: 24px 28px !important;
  border-radius: 18px !important;
  background: linear-gradient(135deg, #eff6ff 0%, #ecfdf5 100%) !important;
  border: 1.5px solid #bfdbfe !important;
  margin-bottom: 20px !important;
}

.sd-dashboard .sd-sub-activity-item {
  border-radius: 12px !important;
  border: 1.5px solid #e2e8f0 !important;
  background: #ffffff !important;
  padding: 14px 18px !important;
  margin-bottom: 10px !important;
  transition: all 0.2s ease !important;
}

.sd-dashboard .sd-sub-activity-item:hover {
  background: #f8fafc !important;
  border-color: #cbd5e1 !important;
  transform: translateX(3px) !important;
}

.sd-dashboard :is(.sd-acc-check-box, .sd-acc-tax-card, .sd-acc-mix-card, .sd-acc-bucket-box) {
  border-radius: 14px !important;
  border: 1.5px solid #e2e8f0 !important;
  background: #ffffff !important;
  padding: 16px !important;
  box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03) !important;
}

/* 15. Dashboard Footer */
.sd-dashboard .sd-footer {
  text-align: center !important;
  font-size: 12px !important;
  color: #94a3b8 !important;
  padding: 24px 0 8px 0 !important;
  border-top: 1px solid #e2e8f0 !important;
  margin-top: 16px !important;
}

/* 16. Responsive Breakpoints */
@media (max-width: 1100px) {
  .sd-dashboard .sd-acc-card-chips {
    grid-template-columns: repeat(3, 1fr) !important;
  }
}

@media (max-width: 768px) {
  .sd-dashboard {
    padding: 0 16px 32px 16px !important;
  }
  .sd-switcher-bar {
    margin: 0 -16px 10px -16px !important;
    width: calc(100% + 32px) !important;
    padding: 8px 16px !important;
  }
  .sd-dashboard .sd-hero {
    padding: 24px 20px !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 16px !important;
  }
  .sd-dashboard .sd-hero-actions {
    width: 100% !important;
    justify-content: space-between !important;
  }
  .sd-dashboard .sd-controls {
    padding: 16px !important;
  }
  .sd-dashboard .sd-acc-card-header {
    flex-direction: column !important;
    align-items: flex-start !important;
    gap: 10px !important;
  }
  .sd-dashboard .sd-acc-card-chips {
    grid-template-columns: repeat(2, 1fr) !important;
  }
  .sd-dashboard .sd-tabs {
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
  }
  .sd-dashboard .sd-tabs button {
    flex: 0 0 auto !important;
  }
}

@media (max-width: 480px) {
  .sd-dashboard .sd-acc-card-chips {
    grid-template-columns: 1fr !important;
  }
}
"""

full_css = base_css + dashboard_theme_css

# Write to target css file
target_path = "sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css"
with open(target_path, "w", encoding="utf-8") as f:
    f.write(full_css)

print("Successfully generated clean single-column sarathi_dashboard.css")
print(f"Total lines: {len(full_css.splitlines())}")
