import sys

target_css = r'sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css'
with open(target_css, encoding='utf-8') as f:
    content = f.read()

split_marker = '.sd-dashboard :is(.sd-card-icon,.sd-setup-icon) { color: var(--metric-ink); background: var(--metric-soft); border-radius: 11px; }'

if split_marker not in content:
    print(f"Error: Split marker not found in {target_css}")
    sys.exit(1)

parts = content.split(split_marker)
base_css = parts[0]

font_import = "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Outfit:wght@500;600;700;800;900&family=JetBrains+Mono:wght@500;600;700;800&display=swap');\n\n"
if '@import url' not in base_css:
    base_css = font_import + base_css

master_theme = '''/* ==========================================================================
   SARATHI CONTROL TOWER · MASTER UNIFIED INDUSTRIAL THEME & DESIGN SYSTEM
   Ultra-modern, colorful, well-formatted cards with distinct borders,
   glowing hover states, no text truncation, and zero layout cutting
   ========================================================================== */

/* 1. Global Page Resets & Zero-Bleed Frappe Overrides */
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
}

[data-page-route="sarathicontroltower"] .page-head {
  display: none !important;
}

/* 2. Master App Outer Wrapper */
.sod-wrapper {
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif !important;
  color: #0f172a !important;
  background: #f8fafc !important;
  min-height: 100vh !important;
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  display: flex !important;
  flex-direction: column !important;
  position: relative !important;
}

.sod-wrapper * {
  box-sizing: border-box !important;
}

/* 3. Top View Switcher Bar */
.sod-switcher-bar {
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  background: #090e17 !important;
  padding: 8px 24px !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  color: #cbd5e1 !important;
  width: 100% !important;
  box-sizing: border-box !important;
  flex-shrink: 0 !important;
  min-height: 44px !important;
}

.sod-switcher-label {
  font-size: 11px !important;
  font-weight: 850 !important;
  text-transform: uppercase !important;
  letter-spacing: 1.5px !important;
  color: #64748b !important;
}

.sod-switcher-btn {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  background: rgba(255, 255, 255, 0.07) !important;
  border: 1px solid rgba(255, 255, 255, 0.14) !important;
  color: #cbd5e1 !important;
  padding: 5px 14px !important;
  border-radius: 12px !important;
  font-size: 12px !important;
  font-weight: 750 !important;
  cursor: pointer !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.sod-switcher-btn:hover {
  background: rgba(255, 255, 255, 0.15) !important;
  color: #ffffff !important;
  transform: translateY(-1px) !important;
}

.sod-switcher-btn.active {
  background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%) !important;
  border-color: transparent !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
}

.sod-switcher-icon {
  font-size: 14px !important;
}

/* 4. App Main Layout Grid (Sidebar + Main Content) */
.sod-app {
  display: grid !important;
  grid-template-columns: 270px minmax(0, 1fr) !important;
  min-height: calc(100vh - 44px) !important;
  width: 100% !important;
  max-width: 100% !important;
  box-sizing: border-box !important;
  position: relative !important;
  align-items: start !important;
}

/* 5. Left Navigation Sidebar */
.sod-side {
  background: radial-gradient(circle at top left, #0e2a38, transparent 40%),
              radial-gradient(circle at bottom, #0f172a, #020617 80%) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
  color: #e2e8f0 !important;
  display: flex !important;
  flex-direction: column !important;
  position: sticky !important;
  top: 0 !important;
  height: calc(100vh - 44px) !important;
  overflow-y: auto !important;
  flex-shrink: 0 !important;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.15) !important;
  z-index: 10 !important;
}

.sod-brand {
  padding: 22px 20px !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 15px !important;
  font-weight: 850 !important;
  letter-spacing: 1.5px !important;
  color: #38bdf8 !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.07) !important;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.03) 0%, transparent 100%) !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 3px !important;
}

.sod-brand small {
  font-size: 9.5px !important;
  color: #94a3b8 !important;
  letter-spacing: 2px !important;
  font-weight: 700 !important;
}

/* Sidebar Navigation Items */
.sod-nav.sd-tabs {
  padding: 14px 10px !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 5px !important;
  background: transparent !important;
  border: none !important;
  margin: 0 !important;
  box-shadow: none !important;
  border-radius: 0 !important;
}

.sod-nav.sd-tabs button {
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  padding: 9px 12px !important;
  border-radius: 12px !important;
  background: transparent !important;
  color: #94a3b8 !important;
  border: 1px solid transparent !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  text-align: left !important;
  width: 100% !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  cursor: pointer !important;
  position: relative !important;
  box-sizing: border-box !important;
}

.sod-nav.sd-tabs button:hover {
  background: rgba(255, 255, 255, 0.06) !important;
  color: #ffffff !important;
  transform: translateX(3px) !important;
}

.sod-nav.sd-tabs button .sarathi-ui-icon {
  width: 18px !important;
  height: 18px !important;
  padding: 6px !important;
  box-sizing: content-box !important;
  border-radius: 9px !important;
  background: rgba(255, 255, 255, 0.06) !important;
  color: #94a3b8 !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  flex-shrink: 0 !important;
  transition: all 0.2s ease !important;
}

.sod-nav.sd-tabs button:hover .sarathi-ui-icon {
  background: rgba(255, 255, 255, 0.12) !important;
  color: #ffffff !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
}

/* Individual Per-Section Glowing Colors */
.sod-nav.sd-tabs button[data-tab="overview"] {
  --tab-accent: #0284c7;
  --tab-glow: rgba(2, 132, 199, 0.35);
  --tab-bg: linear-gradient(135deg, rgba(2, 132, 199, 0.25) 0%, rgba(56, 189, 248, 0.15) 100%);
}
.sod-nav.sd-tabs button[data-tab="subcontracting"] {
  --tab-accent: #0284c7;
  --tab-glow: rgba(2, 132, 199, 0.35);
  --tab-bg: linear-gradient(135deg, rgba(2, 132, 199, 0.25) 0%, rgba(13, 148, 136, 0.15) 100%);
}
.sod-nav.sd-tabs button[data-tab="accounting"] {
  --tab-accent: #059669;
  --tab-glow: rgba(5, 150, 105, 0.35);
  --tab-bg: linear-gradient(135deg, rgba(5, 150, 105, 0.25) 0%, rgba(16, 185, 129, 0.15) 100%);
}
.sod-nav.sd-tabs button[data-tab="sales"] {
  --tab-accent: #f43f5e;
  --tab-glow: rgba(244, 63, 94, 0.35);
  --tab-bg: linear-gradient(135deg, rgba(244, 63, 94, 0.25) 0%, rgba(251, 146, 60, 0.15) 100%);
}
.sod-nav.sd-tabs button[data-tab="production"] {
  --tab-accent: #10b981;
  --tab-glow: rgba(16, 185, 129, 0.35);
  --tab-bg: linear-gradient(135deg, rgba(16, 185, 129, 0.25) 0%, rgba(20, 184, 166, 0.15) 100%);
}
.sod-nav.sd-tabs button[data-tab="engineering"] {
  --tab-accent: #8b5cf6;
  --tab-glow: rgba(139, 92, 246, 0.35);
  --tab-bg: linear-gradient(135deg, rgba(139, 92, 246, 0.25) 0%, rgba(168, 85, 247, 0.15) 100%);
}
.sod-nav.sd-tabs button[data-tab="materials"] {
  --tab-accent: #d97706;
  --tab-glow: rgba(217, 119, 6, 0.35);
  --tab-bg: linear-gradient(135deg, rgba(217, 119, 6, 0.25) 0%, rgba(245, 158, 11, 0.15) 100%);
}
.sod-nav.sd-tabs button[data-tab="procurement"] {
  --tab-accent: #0891b2;
  --tab-glow: rgba(8, 145, 178, 0.35);
  --tab-bg: linear-gradient(135deg, rgba(8, 145, 178, 0.25) 0%, rgba(6, 182, 212, 0.15) 100%);
}
.sod-nav.sd-tabs button[data-tab="quality"] {
  --tab-accent: #db2777;
  --tab-glow: rgba(219, 39, 119, 0.35);
  --tab-bg: linear-gradient(135deg, rgba(219, 39, 119, 0.25) 0%, rgba(236, 72, 153, 0.15) 100%);
}
.sod-nav.sd-tabs button[data-tab="fulfillment"] {
  --tab-accent: #4f46e5;
  --tab-glow: rgba(79, 70, 229, 0.35);
  --tab-bg: linear-gradient(135deg, rgba(79, 70, 229, 0.25) 0%, rgba(99, 102, 241, 0.15) 100%);
}
.sod-nav.sd-tabs button[data-tab="reports"] {
  --tab-accent: #0d9488;
  --tab-glow: rgba(13, 148, 136, 0.35);
  --tab-bg: linear-gradient(135deg, rgba(13, 148, 136, 0.25) 0%, rgba(20, 184, 166, 0.15) 100%);
}
.sod-nav.sd-tabs button[data-tab="integrations"] {
  --tab-accent: #475569;
  --tab-glow: rgba(71, 85, 105, 0.35);
  --tab-bg: linear-gradient(135deg, rgba(51, 65, 85, 0.25) 0%, rgba(71, 85, 105, 0.15) 100%);
}

.sod-nav.sd-tabs button.active {
  background: var(--tab-bg, linear-gradient(135deg, rgba(2, 132, 199, 0.25) 0%, rgba(13, 148, 136, 0.18) 100%)) !important;
  color: #ffffff !important;
  border-color: var(--tab-accent, #38bdf8) !important;
  box-shadow: 0 4px 16px var(--tab-glow, rgba(2, 132, 199, 0.3)), inset 0 1px 1px rgba(255, 255, 255, 0.2) !important;
}

.sod-nav.sd-tabs button.active .sarathi-ui-icon {
  background: var(--tab-accent, #0284c7) !important;
  color: #ffffff !important;
  border-color: transparent !important;
  box-shadow: 0 0 14px var(--tab-accent, #0284c7) !important;
}

.sod-nav.sd-tabs button.active::after {
  content: "" !important;
  position: absolute !important;
  right: -10px !important;
  top: 50% !important;
  transform: translateY(-50%) !important;
  width: 4px !important;
  height: 22px !important;
  border-radius: 4px 0 0 4px !important;
  background: var(--tab-accent, #38bdf8) !important;
  box-shadow: 0 0 10px var(--tab-accent, #38bdf8) !important;
}

/* 6. Main Content Area */
.sod-main {
  padding: 24px 32px 60px !important;
  background: radial-gradient(ellipse at 10% 8%, rgba(14, 165, 233, 0.08) 0%, transparent 45%),
              radial-gradient(ellipse at 90% 15%, rgba(99, 102, 241, 0.07) 0%, transparent 45%),
              radial-gradient(ellipse at 50% 80%, rgba(16, 185, 129, 0.06) 0%, transparent 50%),
              #f8fafc !important;
  min-height: calc(100vh - 44px) !important;
  box-sizing: border-box !important;
  overflow-y: auto !important;
}

/* 7. Topbar with Socket Status & User Pill */
.sod-top {
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  margin-bottom: 20px !important;
  flex-wrap: wrap !important;
  gap: 12px !important;
}

.sod-breadcrumb {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  color: #64748b !important;
}

.sod-breadcrumb a,
.sod-link {
  color: #0284c7 !important;
  text-decoration: none !important;
  font-weight: 700 !important;
}

.sod-breadcrumb a:hover,
.sod-link:hover {
  text-decoration: underline !important;
}

.sod-live-status-pill {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  background: rgba(16, 185, 129, 0.1) !important;
  border: 1px solid rgba(16, 185, 129, 0.3) !important;
  padding: 5px 12px !important;
  border-radius: 20px !important;
  font-size: 11px !important;
  font-weight: 800 !important;
  letter-spacing: 0.8px !important;
  color: #059669 !important;
}

.sod-pulse-dot {
  width: 7px !important;
  height: 7px !important;
  border-radius: 50% !important;
  background: #10b981 !important;
  box-shadow: 0 0 8px #10b981 !important;
  animation: pulse-dot 2s infinite ease-in-out !important;
}

@keyframes pulse-dot {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.4; transform: scale(0.8); }
}

.sod-user-pill {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  background: #ffffff !important;
  border: 1px solid #cbd5e1 !important;
  padding: 4px 10px !important;
  border-radius: 20px !important;
  font-size: 11.5px !important;
  font-weight: 750 !important;
  color: #475569 !important;
}

.sod-avatar {
  display: inline-grid !important;
  place-items: center !important;
  width: 24px !important;
  height: 24px !important;
  border-radius: 50% !important;
  background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%) !important;
  color: #ffffff !important;
  font-size: 10px !important;
  font-weight: 800 !important;
}

/* 8. Hero Gradient Banner */
.sod-hero,
.sd-hero {
  position: relative !important;
  overflow: hidden !important;
  border-radius: 22px !important;
  padding: 28px 34px !important;
  background: linear-gradient(135deg, #090e17 0%, #0c2331 35%, #0f3b4c 70%, #1e1b4b 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.14) !important;
  box-shadow: 0 20px 40px -10px rgba(15, 23, 42, 0.35) !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  flex-wrap: wrap !important;
  gap: 18px !important;
  color: #ffffff !important;
  margin-bottom: 22px !important;
}

.sod-hero::before,
.sd-hero::before {
  content: "" !important;
  position: absolute !important;
  top: -100px !important;
  right: -50px !important;
  width: 400px !important;
  height: 400px !important;
  border-radius: 50% !important;
  background: radial-gradient(circle, rgba(14, 165, 233, 0.28) 0%, rgba(99, 102, 241, 0.16) 50%, transparent 70%) !important;
  pointer-events: none !important;
}

.sod-eyebrow,
.sd-eyebrow {
  display: inline-block !important;
  font-size: 10.5px !important;
  letter-spacing: 2px !important;
  font-weight: 850 !important;
  color: #38bdf8 !important;
  background: rgba(56, 189, 248, 0.12) !important;
  border: 1px solid rgba(56, 189, 248, 0.3) !important;
  padding: 3px 12px !important;
  border-radius: 12px !important;
  margin-bottom: 8px !important;
  text-transform: uppercase !important;
}

.sod-hero h1,
.sd-hero h1 {
  font-family: 'Outfit', sans-serif !important;
  font-size: clamp(26px, 2.5vw, 36px) !important;
  font-weight: 850 !important;
  letter-spacing: -0.6px !important;
  margin: 6px 0 !important;
  color: #ffffff !important;
}

.sod-hero p,
.sd-hero p {
  color: #cbd5e1 !important;
  font-size: 14px !important;
  max-width: 720px !important;
  line-height: 1.55 !important;
  margin: 0 !important;
}

.sod-hero-actions,
.sd-hero-actions {
  display: flex !important;
  align-items: center !important;
  flex-wrap: wrap !important;
  gap: 10px !important;
}

.sod-btn,
.sd-button {
  background: #ffffff !important;
  color: #334155 !important;
  border: 1.5px solid #cbd5e1 !important;
  padding: 8px 16px !important;
  border-radius: 10px !important;
  font-size: 12px !important;
  font-weight: 750 !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
  transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
  cursor: pointer !important;
}

.sod-btn:hover,
.sd-button:hover {
  background: #f8fafc !important;
  color: #0284c7 !important;
  border-color: #0284c7 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.18) !important;
}

.sod-btn-glass {
  background: rgba(255, 255, 255, 0.1) !important;
  border: 1px solid rgba(255, 255, 255, 0.2) !important;
  color: #ffffff !important;
}

.sod-btn-glass:hover {
  background: rgba(255, 255, 255, 0.2) !important;
  color: #ffffff !important;
}

.sod-btn-primary,
.sd-primary {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
  color: #ffffff !important;
  border-color: transparent !important;
  box-shadow: 0 3px 10px rgba(2, 132, 199, 0.3) !important;
}

.sod-btn-primary:hover,
.sd-primary:hover {
  background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
  color: #ffffff !important;
}

.sd-ai-header-btn {
  background: linear-gradient(135deg, #7c3aed 0%, #c026d3 100%) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35) !important;
  font-weight: 750 !important;
}

/* 9. Floating Glass Filter Toolbar */
.sod-filters,
.sd-controls {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px) !important;
  border: 1.5px solid rgba(226, 232, 240, 0.9) !important;
  border-radius: 18px !important;
  padding: 18px 24px !important;
  margin: 20px 0 !important;
  box-shadow: 0 10px 30px -4px rgba(15, 23, 42, 0.05) !important;
  display: flex !important;
  gap: 16px !important;
  flex-wrap: wrap !important;
  align-items: flex-end !important;
}

.sod-filter-group {
  display: flex !important;
  flex-direction: column !important;
  gap: 6px !important;
}

.sod-filter-group label,
.sd-controls label {
  font-size: 11px !important;
  font-weight: 800 !important;
  color: #475569 !important;
  letter-spacing: 0.6px !important;
  text-transform: uppercase !important;
}

.sod-select,
.sod-input,
.sd-controls :is(input, select) {
  background: #f8fafc !important;
  border: 1.5px solid #cbd5e1 !important;
  border-radius: 11px !important;
  padding: 8px 12px !important;
  font-size: 12.5px !important;
  font-weight: 600 !important;
  color: #0f172a !important;
  height: 40px !important;
  transition: all 0.18s ease !important;
}

.sod-select:hover,
.sod-input:hover,
.sd-controls :is(input, select):hover {
  background: #ffffff !important;
  border-color: #94a3b8 !important;
}

.sod-select:focus,
.sod-input:focus,
.sd-controls :is(input, select):focus {
  background: #ffffff !important;
  border-color: #0284c7 !important;
  box-shadow: 0 0 0 3.5px rgba(2, 132, 199, 0.16) !important;
  outline: none !important;
}

.sod-search-group input,
.sd-search input {
  min-width: 220px !important;
}

/* ==========================================================================
   10. MASTER CARD SYSTEM - FULL WIDTH, VIBRANT, WELL-FORMATTED, NO CUTTING
   ========================================================================== */

/* Full Width Card Containers for Subcontracting & Accounting Panels */
[data-subcontracting-cards],
[data-accounting-cards] {
  display: block !important;
  width: 100% !important;
}

/* 10A. FINANCE & ACCOUNTING EXECUTIVE CARD (Full Width & Rich Layout) */
.sd-accounting-main-card {
  position: relative !important;
  overflow: hidden !important;
  text-align: left !important;
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 20px !important;
  padding: 28px 32px !important;
  cursor: pointer !important;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05) !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 16px !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.sd-accounting-main-card:hover {
  transform: translateY(-4px) !important;
  box-shadow: 0 20px 40px -8px rgba(16, 185, 129, 0.18), 0 0 24px rgba(16, 185, 129, 0.12) !important;
  border-color: #10b981 !important;
}

.sd-acc-card-top-strip {
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  height: 5px !important;
  background: linear-gradient(90deg, #0284c7 0%, #10b981 35%, #8b5cf6 70%, #f59e0b 100%) !important;
}

.sd-acc-card-header {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  gap: 18px !important;
  flex-wrap: wrap !important;
  width: 100% !important;
}

.sd-acc-card-title-wrap {
  display: flex !important;
  align-items: center !important;
  gap: 14px !important;
}

.sd-acc-card-icon {
  display: inline-grid !important;
  place-items: center !important;
  width: 46px !important;
  height: 46px !important;
  border-radius: 13px !important;
  background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.3) !important;
  flex-shrink: 0 !important;
}

.sd-acc-card-icon .sarathi-ui-icon {
  width: 22px !important;
  height: 22px !important;
  stroke: #ffffff !important;
}

.sd-acc-card-tag {
  font-size: 11px !important;
  font-weight: 850 !important;
  letter-spacing: 1.2px !important;
  color: #059669 !important;
  margin-bottom: 3px !important;
  text-transform: uppercase !important;
}

.sd-acc-card-title-wrap h3 {
  font-family: 'Outfit', sans-serif !important;
  margin: 0 !important;
  font-size: 22px !important;
  font-weight: 850 !important;
  color: #0f172a !important;
  letter-spacing: -0.4px !important;
  white-space: nowrap !important;
}

.sd-acc-card-header .sd-pill {
  padding: 8px 18px !important;
  font-size: 13px !important;
  font-weight: 850 !important;
  border-radius: 20px !important;
  white-space: nowrap !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04) !important;
}

.sd-acc-card-main-val {
  display: flex !important;
  flex-direction: column !important;
  gap: 4px !important;
  padding: 6px 0 !important;
}

.sd-acc-card-main-val small {
  font-size: 11px !important;
  font-weight: 800 !important;
  color: #64748b !important;
  text-transform: uppercase !important;
  letter-spacing: 0.8px !important;
}

.sd-acc-card-main-val strong {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 34px !important;
  font-weight: 900 !important;
  letter-spacing: -0.8px !important;
  line-height: 1.1 !important;
}

.sd-acc-positive {
  color: #059669 !important;
}

.sd-acc-negative {
  color: #dc2626 !important;
}

/* Stat Chips Grid on Main Card - 6 Columns Across Desktop */
.sd-acc-card-chips {
  display: grid !important;
  grid-template-columns: repeat(6, 1fr) !important;
  gap: 14px !important;
  margin-top: 10px !important;
  width: 100% !important;
}

@media (max-width: 1250px) {
  .sd-acc-card-chips {
    grid-template-columns: repeat(3, 1fr) !important;
  }
}

@media (max-width: 650px) {
  .sd-acc-card-chips {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}

.sd-acc-chip {
  display: flex !important;
  flex-direction: column !important;
  padding: 12px 16px !important;
  border-radius: 14px !important;
  border: 1.5px solid !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  cursor: pointer !important;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03) !important;
}

.sd-acc-chip:hover {
  transform: translateY(-3px) !important;
  box-shadow: 0 8px 18px rgba(0, 0, 0, 0.08) !important;
}

.sd-acc-chip span {
  font-size: 11px !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  opacity: 0.9 !important;
  margin-bottom: 4px !important;
}

.sd-acc-chip b {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 16px !important;
  font-weight: 850 !important;
  letter-spacing: -0.3px !important;
}

/* Distinct Vibrant Colors for Stat Chips */
.sd-acc-chip-blue {
  background: #f0f9ff !important;
  border-color: #7dd3fc !important;
  color: #0369a1 !important;
}
.sd-acc-chip-rose {
  background: #fff1f2 !important;
  border-color: #fda4af !important;
  color: #be123c !important;
}
.sd-acc-chip-amber {
  background: #fffbeb !important;
  border-color: #fcd34d !important;
  color: #b45309 !important;
}
.sd-acc-chip-crimson {
  background: #fff7ed !important;
  border-color: #fdba74 !important;
  color: #c2410c !important;
}
.sd-acc-chip-teal {
  background: #ecfdf5 !important;
  border-color: #6ee7b7 !important;
  color: #047857 !important;
}
.sd-acc-chip-purple {
  background: #faf5ff !important;
  border-color: #d8b4fe !important;
  color: #6b21a8 !important;
}

.sd-acc-card-footer {
  display: flex !important;
  align-items: center !important;
  justify-content: space-between !important;
  border-top: 1px solid #f1f5f9 !important;
  padding-top: 16px !important;
  margin-top: 12px !important;
  font-size: 12.5px !important;
  font-weight: 600 !important;
  color: #64748b !important;
  flex-wrap: wrap !important;
  gap: 12px !important;
}

.sd-acc-card-footer small {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  font-size: 12.5px !important;
  font-weight: 800 !important;
  color: #0284c7 !important;
  background: #f0f9ff !important;
  border: 1px solid #bae6fd !important;
  padding: 5px 14px !important;
  border-radius: 20px !important;
  transition: all 0.2s ease !important;
}

.sd-accounting-main-card:hover .sd-acc-card-footer small {
  background: #0284c7 !important;
  color: #ffffff !important;
  transform: translateX(3px) !important;
}

/* 10B. SUBCONTRACTING OPERATIONS EXECUTIVE CARD */
.sd-subcontracting-main-card {
  position: relative !important;
  overflow: hidden !important;
  text-align: left !important;
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 20px !important;
  padding: 28px 32px !important;
  cursor: pointer !important;
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05) !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 16px !important;
  width: 100% !important;
  box-sizing: border-box !important;
}

.sd-subcontracting-main-card::before {
  content: "" !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  height: 5px !important;
  background: linear-gradient(90deg, #0284c7 0%, #0d9488 40%, #7c3aed 80%, #f59e0b 100%) !important;
}

.sd-subcontracting-main-card:hover {
  transform: translateY(-4px) !important;
  border-color: #0284c7 !important;
  box-shadow: 0 20px 40px -8px rgba(2, 132, 199, 0.18), 0 0 24px rgba(2, 132, 199, 0.12) !important;
}

.sd-subcontracting-main-card .sd-card-icon {
  display: inline-grid !important;
  place-items: center !important;
  width: 46px !important;
  height: 46px !important;
  border-radius: 13px !important;
  background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%) !important;
  color: #ffffff !important;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.3) !important;
  margin-bottom: 2px !important;
}

.sd-subcontracting-main-card .sd-card-icon .sarathi-ui-icon {
  width: 22px !important;
  height: 22px !important;
  stroke: #ffffff !important;
}

.sd-subcontracting-main-card h3 {
  font-family: 'Outfit', sans-serif !important;
  font-size: 22px !important;
  font-weight: 850 !important;
  color: #0f172a !important;
  margin: 0 !important;
  white-space: nowrap !important;
}

.sd-subcontracting-main-card p {
  font-size: 14px !important;
  color: #475569 !important;
  margin: 4px 0 !important;
}

.sd-subcontracting-main-card p.sd-sub-card-mat {
  font-size: 15px !important;
  color: #0369a1 !important;
}

.sd-subcontracting-main-card p.sd-sub-card-mat b {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 18px !important;
  font-weight: 850 !important;
  color: #0284c7 !important;
}

.sd-subcontracting-main-card small {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  font-size: 12.5px !important;
  font-weight: 800 !important;
  color: #0284c7 !important;
  background: #f0f9ff !important;
  border: 1px solid #bae6fd !important;
  padding: 5px 14px !important;
  border-radius: 20px !important;
  width: fit-content !important;
  margin-top: 6px !important;
  transition: all 0.2s ease !important;
}

.sd-subcontracting-main-card:hover small {
  background: #0284c7 !important;
  color: #ffffff !important;
  transform: translateX(3px) !important;
}

/* 10C. CUSTOMER & PROJECT MULTI-CARD GRIDS */
[data-customers],
[data-projects] {
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)) !important;
  gap: 18px !important;
  width: 100% !important;
}

.sd-cards .sd-card {
  position: relative !important;
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 18px !important;
  padding: 22px 24px !important;
  box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04) !important;
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
  cursor: pointer !important;
  text-align: left !important;
  overflow: hidden !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 8px !important;
  min-height: 180px !important;
  box-sizing: border-box !important;
}

.sd-cards .sd-card::before {
  content: "" !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  height: 4.5px !important;
  background: var(--card-accent, linear-gradient(90deg, #0284c7, #38bdf8)) !important;
}

/* 6 Alternating Colorful Schemes for Customer & Project Cards */
.sd-cards .sd-card:nth-child(6n+1) {
  --card-accent: linear-gradient(90deg, #0284c7, #38bdf8);
  --card-glow: rgba(2, 132, 199, 0.2);
  --card-border: #7dd3fc;
  --icon-bg: #f0f9ff;
  --icon-color: #0284c7;
}
.sd-cards .sd-card:nth-child(6n+2) {
  --card-accent: linear-gradient(90deg, #059669, #10b981);
  --card-glow: rgba(16, 185, 129, 0.2);
  --card-border: #6ee7b7;
  --icon-bg: #ecfdf5;
  --icon-color: #059669;
}
.sd-cards .sd-card:nth-child(6n+3) {
  --card-accent: linear-gradient(90deg, #6366f1, #8b5cf6);
  --card-glow: rgba(99, 102, 241, 0.2);
  --card-border: #a5b4fc;
  --icon-bg: #eef2ff;
  --icon-color: #6366f1;
}
.sd-cards .sd-card:nth-child(6n+4) {
  --card-accent: linear-gradient(90deg, #d97706, #f59e0b);
  --card-glow: rgba(245, 158, 11, 0.2);
  --card-border: #fcd34d;
  --icon-bg: #fffbeb;
  --icon-color: #d97706;
}
.sd-cards .sd-card:nth-child(6n+5) {
  --card-accent: linear-gradient(90deg, #e11d48, #f43f5e);
  --card-glow: rgba(225, 29, 72, 0.2);
  --card-border: #fda4af;
  --icon-bg: #fff1f2;
  --icon-color: #e11d48;
}
.sd-cards .sd-card:nth-child(6n+6) {
  --card-accent: linear-gradient(90deg, #0d9488, #14b8a6);
  --card-glow: rgba(13, 148, 136, 0.2);
  --card-border: #99f6e4;
  --icon-bg: #f0fdfa;
  --icon-color: #0d9488;
}

.sd-cards .sd-card:hover {
  transform: translateY(-4px) !important;
  border-color: var(--card-border, #38bdf8) !important;
  box-shadow: 0 16px 32px -4px rgba(15, 23, 42, 0.1), 0 0 20px var(--card-glow, rgba(2, 132, 199, 0.15)) !important;
}

.sd-cards .sd-card .sd-card-icon {
  display: inline-grid !important;
  place-items: center !important;
  width: 42px !important;
  height: 42px !important;
  border-radius: 12px !important;
  background: var(--icon-bg, #f0f9ff) !important;
  color: var(--icon-color, #0284c7) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 14px !important;
  font-weight: 850 !important;
  margin-bottom: 4px !important;
  border: 1px solid rgba(0, 0, 0, 0.05) !important;
}

.sd-cards .sd-card h3 {
  font-family: 'Outfit', sans-serif !important;
  font-size: 16.5px !important;
  font-weight: 850 !important;
  color: #0f172a !important;
  margin: 0 !important;
  line-height: 1.35 !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
  white-space: nowrap !important;
}

.sd-cards .sd-card p {
  font-size: 12.5px !important;
  color: #475569 !important;
  margin: 0 !important;
  line-height: 1.4 !important;
}

.sd-cards .sd-card small {
  font-size: 11.5px !important;
  font-weight: 750 !important;
  color: #0284c7 !important;
  margin-top: auto !important;
  padding-top: 8px !important;
  transition: transform 0.18s ease !important;
  display: inline-block !important;
}

.sd-cards .sd-card:hover small {
  transform: translateX(4px) !important;
  color: #0369a1 !important;
}

/* Progress bar inside project cards */
.sd-progress {
  height: 8px !important;
  background: #e2e8f0 !important;
  border-radius: 8px !important;
  overflow: hidden !important;
  margin: 6px 0 !important;
}

.sd-progress i {
  display: block !important;
  height: 100% !important;
  background: linear-gradient(90deg, #0284c7 0%, #38bdf8 100%) !important;
  border-radius: 8px !important;
  transition: width 0.4s ease !important;
}

/* 10D. SUMMARY KPI STRIP CARDS (5 Radiant Color Themes) */
.sd-kpis {
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)) !important;
  gap: 16px !important;
  margin: 22px 0 !important;
}

.sd-kpi {
  position: relative !important;
  background: #ffffff !important;
  border-radius: 18px !important;
  padding: 22px 24px !important;
  border: 1.5px solid #e2e8f0 !important;
  box-shadow: 0 4px 18px -2px rgba(15, 23, 42, 0.05) !important;
  transition: all 0.24s cubic-bezier(0.4, 0, 0.2, 1) !important;
  overflow: hidden !important;
  text-align: left !important;
  cursor: pointer !important;
  min-height: 140px !important;
  box-sizing: border-box !important;
}

.sd-kpi::before {
  content: "" !important;
  position: absolute !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  height: 4.5px !important;
  background: var(--kpi-accent, linear-gradient(90deg, #0284c7, #38bdf8)) !important;
  border-radius: 18px 18px 0 0 !important;
}

.sd-kpi:hover {
  transform: translateY(-4px) !important;
  border-color: var(--kpi-border, #38bdf8) !important;
  box-shadow: 0 18px 36px -6px rgba(15, 23, 42, 0.12), 0 0 24px var(--kpi-glow, rgba(2, 132, 199, 0.15)) !important;
}

.sd-kpi strong {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: clamp(24px, 2.2vw, 32px) !important;
  font-weight: 850 !important;
  letter-spacing: -0.6px !important;
  color: #0f172a !important;
  margin: 12px 0 6px !important;
  display: block !important;
}

.sd-kpi small {
  font-size: 12px !important;
  font-weight: 550 !important;
  color: #64748b !important;
}

/* 5 Distinctive Color Palettes for KPI slots */
.sd-kpis > .sd-kpi:nth-child(5n+1) {
  --kpi-accent: linear-gradient(90deg, #0284c7, #38bdf8);
  --kpi-border: #7dd3fc;
  --kpi-glow: rgba(2, 132, 199, 0.2);
  --metric-soft: #f0f9ff;
  --metric-ink: #0369a1;
}
.sd-kpis > .sd-kpi:nth-child(5n+2) {
  --kpi-accent: linear-gradient(90deg, #4f46e5, #7c3aed);
  --kpi-border: #a5b4fc;
  --kpi-glow: rgba(79, 70, 229, 0.2);
  --metric-soft: #eef2ff;
  --metric-ink: #4338ca;
}
.sd-kpis > .sd-kpi:nth-child(5n+3) {
  --kpi-accent: linear-gradient(90deg, #059669, #10b981);
  --kpi-border: #6ee7b7;
  --kpi-glow: rgba(16, 185, 129, 0.2);
  --metric-soft: #ecfdf5;
  --metric-ink: #047857;
}
.sd-kpis > .sd-kpi:nth-child(5n+4) {
  --kpi-accent: linear-gradient(90deg, #d97706, #f59e0b);
  --kpi-border: #fcd34d;
  --kpi-glow: rgba(245, 158, 11, 0.2);
  --metric-soft: #fffbeb;
  --metric-ink: #b45309;
}
.sd-kpis > .sd-kpi:nth-child(5n+5) {
  --kpi-accent: linear-gradient(90deg, #e11d48, #f43f5e);
  --kpi-border: #fda4af;
  --kpi-glow: rgba(225, 29, 72, 0.2);
  --metric-soft: #fff1f2;
  --metric-ink: #be123c;
}

/* 11. Live Project Production Pipeline */
.sd-pipeline-project {
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 18px !important;
  padding: 22px 24px !important;
  margin-bottom: 16px !important;
  box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04) !important;
  transition: all 0.22s ease !important;
}

.sd-pipeline-project:hover {
  border-color: #0284c7 !important;
  box-shadow: 0 10px 28px -4px rgba(2, 132, 199, 0.12) !important;
}

.sd-pipeline-project > strong {
  font-family: 'Outfit', sans-serif !important;
  font-size: 15.5px !important;
  font-weight: 850 !important;
  color: #0f172a !important;
  display: block !important;
  margin-bottom: 14px !important;
}

.sd-pipeline-steps {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 10px !important;
  align-items: center !important;
}

.sd-pipeline-step {
  display: inline-flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 9px 15px !important;
  border-radius: 12px !important;
  background: #f1f5f9 !important;
  border: 1.5px solid #cbd5e1 !important;
  color: #475569 !important;
  cursor: pointer !important;
  transition: all 0.18s ease !important;
  min-width: 95px !important;
}

.sd-pipeline-step small {
  font-size: 9.5px !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.6px !important;
  opacity: 0.85 !important;
  margin-bottom: 2px !important;
}

.sd-pipeline-step strong {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 13.5px !important;
  font-weight: 850 !important;
}

.sd-pipeline-step:hover {
  transform: translateY(-2px) !important;
  border-color: #0284c7 !important;
  color: #0284c7 !important;
  background: #f0f9ff !important;
}

.sd-pipeline-step.sd-step-recorded {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
  color: #ffffff !important;
  border-color: transparent !important;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
}

.sd-pipeline-step.sd-step-recorded:hover {
  background: linear-gradient(135deg, #047857 0%, #059669 100%) !important;
  color: #ffffff !important;
}

.sd-pipeline-step.sd-step-restricted {
  background: #f8fafc !important;
  color: #94a3b8 !important;
  border-color: #e2e8f0 !important;
  opacity: 0.7 !important;
  cursor: not-allowed !important;
}

/* 12. Panels & Card Sections */
.sod-panel,
.sd-panel {
  position: relative !important;
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 20px !important;
  padding: 26px 28px !important;
  margin-top: 24px !important;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05) !important;
}

.sod-panel::before,
.sd-panel::before {
  content: "" !important;
  position: absolute !important;
  top: 0 !important;
  left: 24px !important;
  right: 24px !important;
  height: 3px !important;
  background: linear-gradient(90deg, #0284c7 0%, #4f46e5 100%) !important;
  border-radius: 0 0 3px 3px !important;
}

.sd-panel-heading {
  display: flex !important;
  justify-content: space-between !important;
  align-items: flex-start !important;
  flex-wrap: wrap !important;
  gap: 12px !important;
  padding-bottom: 16px !important;
  margin-bottom: 20px !important;
  border-bottom: 1px solid #f1f5f9 !important;
}

.sd-panel-heading h2 {
  font-family: 'Outfit', sans-serif !important;
  font-size: 19px !important;
  font-weight: 850 !important;
  color: #0f172a !important;
  letter-spacing: -0.4px !important;
  margin: 0 0 4px !important;
}

.sd-panel-heading p {
  font-size: 13px !important;
  color: #64748b !important;
  line-height: 1.5 !important;
  margin: 0 !important;
}

/* 13. Unique Charts & Visualizations */
.sd-chart-grid {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)) !important;
  gap: 20px !important;
  margin-top: 18px !important;
}

/* Conic Donut Chart */
.sd-donut-wrap {
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  gap: 18px !important;
  padding: 16px 0 !important;
}

.sd-donut {
  width: 170px !important;
  height: 170px !important;
  border-radius: 50% !important;
  position: relative !important;
  display: grid !important;
  place-items: center !important;
  margin: 0 auto !important;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.08) !important;
}

.sd-donut::after {
  content: "" !important;
  position: absolute !important;
  inset: 28px !important;
  background: #ffffff !important;
  border-radius: 50% !important;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.06) !important;
}

.sd-donut > span {
  position: relative !important;
  z-index: 2 !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 24px !important;
  font-weight: 850 !important;
  color: #0f172a !important;
  text-align: center !important;
}

.sd-donut > span small {
  font-size: 10px !important;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-weight: 750 !important;
  color: #64748b !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  margin-top: 2px !important;
}

.sd-chart-legend {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 8px 12px !important;
  justify-content: center !important;
  align-items: center !important;
  margin-top: 14px !important;
}

.sd-chart-legend span {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  font-size: 11.5px !important;
  font-weight: 650 !important;
  color: #475569 !important;
  background: #f8fafc !important;
  border: 1px solid #e2e8f0 !important;
  padding: 4px 10px !important;
  border-radius: 20px !important;
}

.sd-chart-legend span i {
  width: 9px !important;
  height: 9px !important;
  border-radius: 50% !important;
  display: inline-block !important;
  flex-shrink: 0 !important;
}

.sd-chart-legend span b {
  font-family: 'JetBrains Mono', monospace !important;
  font-weight: 800 !important;
  color: #0f172a !important;
  margin-left: 2px !important;
}

/* SVG Line & Trend Charts */
.sd-panel svg {
  overflow: visible !important;
  width: 100% !important;
  max-height: 240px !important;
}

.sd-panel svg polyline {
  stroke-width: 3px !important;
  stroke-linecap: round !important;
  stroke-linejoin: round !important;
  filter: drop-shadow(0 4px 6px rgba(2, 132, 199, 0.25)) !important;
}

.sd-panel svg text {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 10px !important;
  font-weight: 600 !important;
  fill: #64748b !important;
}

/* Bar Charts */
.sd-bars {
  display: flex !important;
  flex-direction: column !important;
  gap: 12px !important;
  margin-top: 14px !important;
}

.sd-bar-row {
  display: grid !important;
  grid-template-columns: 140px 1fr !important;
  align-items: center !important;
  gap: 12px !important;
}

.sd-bar-row > span {
  font-size: 12px !important;
  font-weight: 700 !important;
  color: #334155 !important;
  white-space: nowrap !important;
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

.sd-bar-track {
  height: 10px !important;
  background: #e2e8f0 !important;
  border-radius: 10px !important;
  overflow: hidden !important;
  position: relative !important;
}

.sd-bar-fill {
  height: 100% !important;
  border-radius: 10px !important;
  background: linear-gradient(90deg, #0284c7 0%, #38bdf8 100%) !important;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* 14. Master Data Tables */
.sd-table-wrap {
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 16px !important;
  background: #ffffff !important;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.04) !important;
  overflow-x: auto !important;
  margin-top: 16px !important;
}

.sd-table {
  width: 100% !important;
  border-collapse: separate !important;
  border-spacing: 0 !important;
}

.sd-table th {
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
  color: #334155 !important;
  font-size: 11px !important;
  font-weight: 850 !important;
  letter-spacing: 0.7px !important;
  text-transform: uppercase !important;
  padding: 14px 18px !important;
  border-bottom: 2px solid #cbd5e1 !important;
  position: sticky !important;
  top: 0 !important;
  z-index: 2 !important;
  white-space: nowrap !important;
}

.sd-table td {
  padding: 13px 18px !important;
  font-size: 12.5px !important;
  color: #1e293b !important;
  border-bottom: 1px solid #f1f5f9 !important;
  vertical-align: middle !important;
  white-space: nowrap !important;
  font-variant-numeric: tabular-nums !important;
}

.sd-table tbody tr:nth-child(even) td {
  background: #fbfcfe !important;
}

.sd-table tbody tr:hover td {
  background: rgba(2, 132, 199, 0.05) !important;
  color: #0f172a !important;
}

/* Status Pills */
.sod-pill,
.sd-pill {
  display: inline-flex !important;
  align-items: center !important;
  gap: 5px !important;
  border-radius: 20px !important;
  padding: 4px 12px !important;
  font-size: 11px !important;
  font-weight: 800 !important;
  letter-spacing: 0.3px !important;
  white-space: nowrap !important;
}

.sod-pill-green,
.sd-pill.sd-status-green {
  background: #ecfdf5 !important;
  color: #065f46 !important;
  border: 1px solid #a7f3d0 !important;
}

.sod-pill-blue,
.sd-pill.sd-status-blue {
  background: #eff6ff !important;
  color: #1e40af !important;
  border: 1px solid #bfdbfe !important;
}

.sod-pill-amber,
.sd-pill.sd-status-amber {
  background: #fffbeb !important;
  color: #92400e !important;
  border: 1px solid #fde68a !important;
}

.sod-pill-red,
.sd-pill.sd-status-red {
  background: #fff1f2 !important;
  color: #be123c !important;
  border: 1px solid #fecdd3 !important;
}

/* 15. Responsive Design */
@media (max-width: 992px) {
  .sod-app {
    grid-template-columns: 1fr !important;
  }
  .sod-side {
    position: relative !important;
    height: auto !important;
    max-height: 240px !important;
  }
  .sod-nav.sd-tabs {
    flex-direction: row !important;
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
  }
  .sod-nav.sd-tabs button {
    flex: 0 0 auto !important;
    width: auto !important;
  }
  .sod-main {
    padding: 16px 14px 40px !important;
  }
  .sd-kpis {
    grid-template-columns: repeat(2, 1fr) !important;
  }
  .sd-chart-grid {
    grid-template-columns: 1fr !important;
  }
}

@media (max-width: 600px) {
  .sod-filters,
  .sd-controls {
    flex-direction: column !important;
    align-items: stretch !important;
  }
  .sod-search-group input,
  .sd-search input {
    min-width: 100% !important;
  }
  .sd-kpis {
    grid-template-columns: 1fr !important;
  }
}
'''

new_css = base_css + split_marker + '\n' + master_theme
with open(target_css, 'w', encoding='utf-8') as f:
    f.write(new_css)

print(f"Successfully compiled unified master theme to {target_css}!")
print(f"Total lines: {len(new_css.splitlines())}, Total bytes: {len(new_css.encode('utf-8'))}")
