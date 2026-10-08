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

# Add Google Fonts import at top if not present
font_import = "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Outfit:wght@500;600;700;800;900&family=JetBrains+Mono:wght@500;600;700;800&display=swap');\n\n"
if '@import url' not in base_css:
    base_css = font_import + base_css

master_theme = '''/* ==========================================================================
   SARATHI CONTROL TOWER · MASTER INDUSTRIAL THEME & DESIGN SYSTEM
   Ultra-modern, colorful, responsive design system across all sections
   ========================================================================== */

/* 1. Global Dashboard Container & Ambient Mesh */
.sd-dashboard {
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  color: #0f172a !important;
  background: radial-gradient(ellipse at 10% 8%, rgba(14, 165, 233, 0.09) 0%, transparent 45%),
              radial-gradient(ellipse at 90% 15%, rgba(99, 102, 241, 0.08) 0%, transparent 45%),
              radial-gradient(ellipse at 50% 80%, rgba(16, 185, 129, 0.07) 0%, transparent 50%),
              #f8fafc !important;
  padding: 24px !important;
  border-radius: 20px !important;
  --sd-accent: #0284c7;
  --sd-accent-end: #4f46e5;
  --sd-soft: #f0f9ff;
  --sd-border: #bae6fd;
}

/* 2. Top View Switcher Bar */
.sd-switcher-bar {
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  background: rgba(255, 255, 255, 0.85) !important;
  backdrop-filter: blur(14px) !important;
  border: 1px solid rgba(226, 232, 240, 0.9) !important;
  border-radius: 14px !important;
  padding: 10px 16px !important;
  margin-bottom: 20px !important;
  flex-wrap: wrap !important;
  box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04) !important;
}
.sd-switcher-label {
  font-size: 11px !important;
  font-weight: 850 !important;
  color: #64748b !important;
  letter-spacing: 0.8px !important;
  text-transform: uppercase !important;
  margin-right: 4px !important;
}
.sd-switcher-btn {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  padding: 8px 16px !important;
  border-radius: 10px !important;
  font-size: 12.5px !important;
  font-weight: 750 !important;
  border: 1.5px solid #cbd5e1 !important;
  background: #ffffff !important;
  color: #334155 !important;
  cursor: pointer !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
}
.sd-switcher-btn:hover {
  transform: translateY(-1px) !important;
  border-color: #0284c7 !important;
  color: #0284c7 !important;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.16) !important;
}
.sd-switcher-btn.active {
  background: linear-gradient(135deg, #0284c7 0%, #0d9488 100%) !important;
  color: #ffffff !important;
  border-color: transparent !important;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
}
.sd-switcher-icon {
  font-size: 15px !important;
}

/* 3. Majestic Hero Header */
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
.sd-hero::before {
  content: "";
  position: absolute;
  top: -100px;
  right: -50px;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(14, 165, 233, 0.28) 0%, rgba(99, 102, 241, 0.16) 50%, transparent 70%);
  pointer-events: none;
}
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
.sd-hero h1 {
  font-family: 'Outfit', sans-serif !important;
  font-size: clamp(26px, 2.5vw, 36px) !important;
  font-weight: 850 !important;
  letter-spacing: -0.6px !important;
  margin: 6px 0 !important;
  color: #ffffff !important;
}
.sd-hero p {
  color: #cbd5e1 !important;
  font-size: 14px !important;
  max-width: 720px !important;
  line-height: 1.55 !important;
  margin: 0 !important;
}
.sd-hero-actions {
  display: flex !important;
  align-items: center !important;
  flex-wrap: wrap !important;
  gap: 10px !important;
}
.sd-hero-actions [data-updated] {
  color: #94a3b8 !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  background: rgba(255, 255, 255, 0.08) !important;
  padding: 6px 12px !important;
  border-radius: 8px !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}
.sd-ai-header-btn {
  background: linear-gradient(135deg, #7c3aed 0%, #c026d3 100%) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35) !important;
  font-weight: 750 !important;
  padding: 8px 16px !important;
  border-radius: 10px !important;
}
.sd-ai-header-btn:hover {
  transform: translateY(-2px) !important;
  box-shadow: 0 6px 18px rgba(124, 58, 237, 0.45) !important;
}

/* 4. Floating Glass Filter Toolbar */
.sd-controls {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px) !important;
  border: 1px solid rgba(226, 232, 240, 0.9) !important;
  border-radius: 18px !important;
  padding: 18px 24px !important;
  margin: 20px 0 !important;
  box-shadow: 0 10px 30px -4px rgba(15, 23, 42, 0.05) !important;
  display: flex !important;
  gap: 16px !important;
  flex-wrap: wrap !important;
  align-items: flex-end !important;
}
.sd-controls label {
  font-size: 11px !important;
  font-weight: 800 !important;
  color: #475569 !important;
  letter-spacing: 0.6px !important;
  text-transform: uppercase !important;
  display: flex !important;
  flex-direction: column !important;
  gap: 6px !important;
}
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
.sd-controls :is(input, select):hover {
  background: #ffffff !important;
  border-color: #94a3b8 !important;
}
.sd-controls :is(input, select):focus {
  background: #ffffff !important;
  border-color: #0284c7 !important;
  box-shadow: 0 0 0 3.5px rgba(2, 132, 199, 0.16) !important;
  outline: none !important;
}
.sd-search input {
  min-width: 220px !important;
}
.sd-date-btn-group {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  height: 40px !important;
}
.sd-date-btn-group .sd-primary {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 750 !important;
  padding: 0 16px !important;
  height: 40px !important;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.28) !important;
}
.sd-date-btn-group .sd-button:not(.sd-primary) {
  background: #ffffff !important;
  border: 1.5px solid #cbd5e1 !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
  padding: 0 14px !important;
  height: 40px !important;
  color: #475569 !important;
}

/* Breadcrumb & Scope Note */
.sd-breadcrumb {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  color: #64748b !important;
  margin: 12px 0 !important;
}
.sd-breadcrumb a {
  color: #0284c7 !important;
  text-decoration: none !important;
  font-weight: 700 !important;
}
.sd-breadcrumb a:hover {
  text-decoration: underline !important;
}
.sd-scope-note {
  font-size: 12px !important;
  color: #64748b !important;
  background: #f1f5f9 !important;
  border-left: 3.5px solid #0284c7 !important;
  padding: 8px 14px !important;
  border-radius: 0 8px 8px 0 !important;
  margin: 10px 0 18px !important;
}

/* 5. Summary KPIs Strip - 5 Vibrant Themes */
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
}
.sd-kpi::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4.5px;
  background: var(--kpi-accent, linear-gradient(90deg, #0284c7, #38bdf8));
  border-radius: 18px 18px 0 0;
}
.sd-kpi:hover {
  transform: translateY(-4px) !important;
  border-color: var(--kpi-border, #38bdf8) !important;
  box-shadow: 0 18px 36px -6px rgba(15, 23, 42, 0.12), 0 0 24px var(--kpi-glow, rgba(2, 132, 199, 0.15)) !important;
}
.sd-kpi-label,
.sd-metric-label {
  display: flex !important;
  align-items: center !important;
  gap: 8px !important;
  font-size: 11.5px !important;
  font-weight: 800 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.6px !important;
  color: #475569 !important;
}
.sd-kpi-value,
.sd-kpi strong {
  font-family: 'JetBrains Mono', 'Plus Jakarta Sans', monospace !important;
  font-size: clamp(24px, 2.2vw, 32px) !important;
  font-weight: 850 !important;
  letter-spacing: -0.6px !important;
  color: #0f172a !important;
  margin: 12px 0 6px !important;
  display: block !important;
}
.sd-kpi small,
.sd-kpi-sub {
  font-size: 12px !important;
  font-weight: 550 !important;
  color: #64748b !important;
}

/* 5 Distinctive Color Palettes for KPI slots */
.sd-kpis > .sd-kpi:nth-child(5n+1),
.sd-dashboard .sd-kpi:nth-child(5n+1) {
  --kpi-accent: linear-gradient(90deg, #0284c7, #38bdf8);
  --kpi-border: #7dd3fc;
  --kpi-glow: rgba(2, 132, 199, 0.2);
  --metric-soft: #f0f9ff;
  --metric-ink: #0369a1;
}
.sd-kpis > .sd-kpi:nth-child(5n+2),
.sd-dashboard .sd-kpi:nth-child(5n+2) {
  --kpi-accent: linear-gradient(90deg, #4f46e5, #7c3aed);
  --kpi-border: #a5b4fc;
  --kpi-glow: rgba(79, 70, 229, 0.2);
  --metric-soft: #eef2ff;
  --metric-ink: #4338ca;
}
.sd-kpis > .sd-kpi:nth-child(5n+3),
.sd-dashboard .sd-kpi:nth-child(5n+3) {
  --kpi-accent: linear-gradient(90deg, #059669, #10b981);
  --kpi-border: #6ee7b7;
  --kpi-glow: rgba(16, 185, 129, 0.2);
  --metric-soft: #ecfdf5;
  --metric-ink: #047857;
}
.sd-kpis > .sd-kpi:nth-child(5n+4),
.sd-dashboard .sd-kpi:nth-child(5n+4) {
  --kpi-accent: linear-gradient(90deg, #d97706, #f59e0b);
  --kpi-border: #fcd34d;
  --kpi-glow: rgba(245, 158, 11, 0.2);
  --metric-soft: #fffbeb;
  --metric-ink: #b45309;
}
.sd-kpis > .sd-kpi:nth-child(5n+5),
.sd-dashboard .sd-kpi:nth-child(5n+5) {
  --kpi-accent: linear-gradient(90deg, #e11d48, #f43f5e);
  --kpi-border: #fda4af;
  --kpi-glow: rgba(225, 29, 72, 0.2);
  --metric-soft: #fff1f2;
  --metric-ink: #be123c;
}

/* 6. Live Project Production Pipeline */
.sd-pipeline-project {
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 16px !important;
  padding: 20px 22px !important;
  margin-bottom: 14px !important;
  box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04) !important;
  transition: all 0.22s ease !important;
}
.sd-pipeline-project:hover {
  border-color: #0284c7 !important;
  box-shadow: 0 8px 24px -4px rgba(2, 132, 199, 0.12) !important;
}
.sd-pipeline-project > strong {
  font-family: 'Outfit', sans-serif !important;
  font-size: 15px !important;
  font-weight: 800 !important;
  color: #0f172a !important;
  display: block !important;
  margin-bottom: 12px !important;
}
.sd-pipeline-steps {
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 8px !important;
  align-items: center !important;
}
.sd-pipeline-step {
  display: inline-flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  padding: 8px 14px !important;
  border-radius: 11px !important;
  background: #f1f5f9 !important;
  border: 1px solid #cbd5e1 !important;
  color: #475569 !important;
  cursor: pointer !important;
  transition: all 0.18s ease !important;
  min-width: 90px !important;
}
.sd-pipeline-step small {
  font-size: 9.5px !important;
  font-weight: 750 !important;
  text-transform: uppercase !important;
  letter-spacing: 0.5px !important;
  opacity: 0.85 !important;
  margin-bottom: 2px !important;
}
.sd-pipeline-step strong {
  font-family: 'JetBrains Mono', monospace !important;
  font-size: 13px !important;
  font-weight: 800 !important;
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

/* 7. Panels & Card Sections */
.sd-panel {
  position: relative !important;
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 18px !important;
  padding: 24px !important;
  margin-top: 22px !important;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05) !important;
}
.sd-panel::before {
  content: "";
  position: absolute;
  top: 0;
  left: 24px;
  right: 24px;
  height: 3px;
  background: linear-gradient(90deg, #0284c7 0%, #4f46e5 100%);
  border-radius: 0 0 3px 3px;
}
.sd-panel-heading {
  display: flex !important;
  justify-content: space-between !important;
  align-items: flex-start !important;
  flex-wrap: wrap !important;
  gap: 12px !important;
  padding-bottom: 14px !important;
  margin-bottom: 18px !important;
  border-bottom: 1px solid #f1f5f9 !important;
}
.sd-panel-heading h2 {
  font-family: 'Outfit', sans-serif !important;
  font-size: 18px !important;
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

/* Card Grids */
.sd-cards {
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)) !important;
  gap: 16px !important;
}
.sd-card {
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  border-radius: 16px !important;
  padding: 20px !important;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03) !important;
  transition: all 0.22s cubic-bezier(0.4, 0, 0.2, 1) !important;
  cursor: pointer !important;
  text-align: left !important;
}
.sd-card:hover {
  transform: translateY(-3px) !important;
  border-color: #0284c7 !important;
  box-shadow: 0 12px 28px -4px rgba(15, 23, 42, 0.1), 0 0 16px rgba(2, 132, 199, 0.15) !important;
}
.sd-card-icon,
.sd-setup-icon {
  display: inline-grid !important;
  place-items: center !important;
  width: 38px !important;
  height: 38px !important;
  border-radius: 11px !important;
  background: #f0f9ff !important;
  color: #0284c7 !important;
  margin-bottom: 10px !important;
}

/* 8. Analysis Workspace Tabs Navigation */
.sd-tabs,
.sd-acc-tabs {
  background: #0f172a !important;
  padding: 8px 10px !important;
  border-radius: 16px !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 6px !important;
  margin: 22px 0 !important;
  box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.3) !important;
}
.sd-tabs button,
.sd-acc-tab-btn {
  display: inline-flex !important;
  align-items: center !important;
  gap: 8px !important;
  background: transparent !important;
  color: #94a3b8 !important;
  border: 1px solid transparent !important;
  border-radius: 10px !important;
  padding: 10px 16px !important;
  font-size: 13px !important;
  font-weight: 700 !important;
  transition: all 0.18s ease !important;
  cursor: pointer !important;
}
.sd-tabs button:hover,
.sd-acc-tab-btn:hover {
  color: #ffffff !important;
  background: rgba(255, 255, 255, 0.1) !important;
}

/* Distinct Glowing Colors on Active Tabs */
.sd-tabs button.active,
.sd-acc-tab-btn.active {
  background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%) !important;
  color: #ffffff !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  box-shadow: 0 4px 16px rgba(2, 132, 199, 0.35) !important;
}
.sd-tabs button[data-tab="overview"].active {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
}
.sd-tabs button[data-tab="sales"].active {
  background: linear-gradient(135deg, #f43f5e 0%, #e11d48 100%) !important;
  box-shadow: 0 4px 14px rgba(244, 63, 94, 0.35) !important;
}
.sd-tabs button[data-tab="production"].active {
  background: linear-gradient(135deg, #059669 0%, #10b981 100%) !important;
  box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35) !important;
}
.sd-tabs button[data-tab="engineering"].active {
  background: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%) !important;
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35) !important;
}
.sd-tabs button[data-tab="materials"].active {
  background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%) !important;
  box-shadow: 0 4px 14px rgba(217, 119, 6, 0.35) !important;
}
.sd-tabs button[data-tab="procurement"].active {
  background: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%) !important;
  box-shadow: 0 4px 14px rgba(8, 145, 178, 0.35) !important;
}
.sd-tabs button[data-tab="quality"].active {
  background: linear-gradient(135deg, #db2777 0%, #ec4899 100%) !important;
  box-shadow: 0 4px 14px rgba(219, 39, 119, 0.35) !important;
}
.sd-tabs button[data-tab="fulfillment"].active {
  background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.35) !important;
}
.sd-tabs button[data-tab="reports"].active {
  background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%) !important;
  box-shadow: 0 4px 14px rgba(13, 148, 136, 0.35) !important;
}
.sd-tabs button[data-tab="integrations"].active {
  background: linear-gradient(135deg, #334155 0%, #475569 100%) !important;
  box-shadow: 0 4px 14px rgba(51, 65, 85, 0.35) !important;
}

/* 9. Unique Charts & Visualizations */
.sd-chart-grid {
  display: grid !important;
  grid-template-columns: repeat(auto-fit, minmax(360px, 1fr)) !important;
  gap: 20px !important;
  margin-top: 18px !important;
}

/* Modern Conic Donut Chart */
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
  content: "";
  position: absolute;
  inset: 28px;
  background: #ffffff;
  border-radius: 50%;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.06);
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

/* Chart Legends */
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

/* 10. Master Data Tables */
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

/* 11. Links, Action Buttons & Badges */
.sd-table a,
.sd-link {
  color: #0284c7 !important;
  font-weight: 700 !important;
  text-decoration: none !important;
  transition: all 0.18s ease !important;
}
.sd-table a:hover,
.sd-link:hover {
  color: #0369a1 !important;
  text-decoration: underline !important;
}
.sd-inspect {
  display: inline-flex !important;
  align-items: center !important;
  padding: 3px 8px !important;
  border-radius: 6px !important;
  font-size: 10.5px !important;
  font-weight: 800 !important;
  background: #f0f9ff !important;
  color: #0284c7 !important;
  border: 1px solid #bae6fd !important;
  cursor: pointer !important;
  margin-left: 6px !important;
  transition: all 0.15s ease !important;
}
.sd-inspect:hover {
  background: #0284c7 !important;
  color: #ffffff !important;
}
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
.sd-button:hover {
  background: #f8fafc !important;
  color: #0284c7 !important;
  border-color: #0284c7 !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.18) !important;
}
.sd-primary {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
  color: #ffffff !important;
  border-color: transparent !important;
  box-shadow: 0 3px 10px rgba(2, 132, 199, 0.3) !important;
}
.sd-primary:hover {
  background: linear-gradient(135deg, #0369a1 0%, #075985 100%) !important;
  color: #ffffff !important;
}
.sd-text-button {
  background: transparent !important;
  border: none !important;
  color: #0284c7 !important;
  font-size: 12.5px !important;
  font-weight: 750 !important;
  cursor: pointer !important;
  transition: all 0.18s ease !important;
}
.sd-text-button:hover {
  color: #0369a1 !important;
  transform: translateX(3px) !important;
}

/* Status Pills */
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
.sd-pill.sd-status-green {
  background: #ecfdf5 !important;
  color: #065f46 !important;
  border: 1px solid #a7f3d0 !important;
}
.sd-pill.sd-status-blue {
  background: #eff6ff !important;
  color: #1e40af !important;
  border: 1px solid #bfdbfe !important;
}
.sd-pill.sd-status-amber {
  background: #fffbeb !important;
  color: #92400e !important;
  border: 1px solid #fde68a !important;
}
.sd-pill.sd-status-red {
  background: #fff1f2 !important;
  color: #be123c !important;
  border: 1px solid #fecdd3 !important;
}
.sd-pill.sd-status-violet {
  background: #f5f3ff !important;
  color: #6d28d9 !important;
  border: 1px solid #ddd6fe !important;
}

/* Pagination */
.sd-pagination {
  display: flex !important;
  align-items: center !important;
  justify-content: flex-end !important;
  gap: 8px !important;
  margin-top: 14px !important;
}
.sd-pagination button {
  padding: 6px 14px !important;
  border-radius: 8px !important;
  font-size: 11.5px !important;
  font-weight: 750 !important;
}

/* 12. Subcontracting & Accounting Deep Components */
.sd-sub-header {
  padding: 24px !important;
  border-radius: 18px !important;
  background: linear-gradient(115deg, #e0f2fe 0%, #f0fdfa 100%) !important;
  border: 1.5px solid #bae6fd !important;
  margin-bottom: 20px !important;
}
.sd-sub-activity-item {
  border-radius: 14px !important;
  border: 1px solid #e2e8f0 !important;
  background: #ffffff !important;
  padding: 14px 18px !important;
  margin-bottom: 10px !important;
  transition: all 0.18s ease !important;
}
.sd-sub-activity-item:hover {
  border-color: #0284c7 !important;
  box-shadow: 0 4px 14px rgba(2, 132, 199, 0.08) !important;
}
.sd-sub-legend-pill {
  display: inline-flex !important;
  align-items: center !important;
  gap: 6px !important;
  padding: 6px 14px !important;
  border-radius: 20px !important;
  font-size: 11.5px !important;
  font-weight: 750 !important;
  background: #ffffff !important;
  border: 1.5px solid #e2e8f0 !important;
  color: #475569 !important;
  cursor: pointer !important;
  transition: all 0.18s ease !important;
}
.sd-sub-legend-pill:hover {
  border-color: #0284c7 !important;
  color: #0284c7 !important;
  transform: translateY(-1px) !important;
}
.sd-sub-legend-pill.active {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
  color: #ffffff !important;
  border-color: transparent !important;
  box-shadow: 0 3px 10px rgba(2, 132, 199, 0.3) !important;
}

/* Accounting Specific Elements */
:is(.sd-acc-check-box, .sd-acc-tax-card, .sd-acc-mix-card, .sd-acc-bucket-box) {
  border-radius: 14px !important;
  border: 1.5px solid #e2e8f0 !important;
  background: #ffffff !important;
  padding: 18px !important;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03) !important;
  transition: all 0.2s ease !important;
}
:is(.sd-acc-check-box, .sd-acc-tax-card, .sd-acc-mix-card, .sd-acc-bucket-box):hover {
  border-color: #10b981 !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.12) !important;
}

/* 13. Footer */
.sd-footer {
  text-align: center !important;
  color: #94a3b8 !important;
  font-size: 12px !important;
  font-weight: 600 !important;
  margin-top: 36px !important;
  padding-top: 20px !important;
  border-top: 1px solid #e2e8f0 !important;
}

/* 14. Responsive Layouts */
@media (max-width: 1200px) {
  .sd-kpis {
    grid-template-columns: repeat(3, 1fr) !important;
  }
  .sd-chart-grid {
    grid-template-columns: 1fr !important;
  }
}
@media (max-width: 800px) {
  .sd-dashboard {
    padding: 14px !important;
  }
  .sd-hero {
    padding: 22px 20px !important;
  }
  .sd-controls {
    flex-direction: column !important;
    align-items: stretch !important;
  }
  .sd-search input {
    min-width: 100% !important;
  }
  .sd-kpis {
    grid-template-columns: repeat(2, 1fr) !important;
  }
  .sd-tabs,
  .sd-acc-tabs {
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
  }
  .sd-tabs button,
  .sd-acc-tab-btn {
    flex-shrink: 0 !important;
  }
}
@media (max-width: 480px) {
  .sd-kpis {
    grid-template-columns: 1fr !important;
  }
  .sd-bar-row {
    grid-template-columns: 100px 1fr !important;
  }
}
'''

new_content = base_css + split_marker + '\n' + master_theme
with open(target_css, 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f"Successfully compiled and written master theme to {target_css}!")
print(f"Total lines: {len(new_content.splitlines())}, Total bytes: {len(new_content.encode('utf-8'))}")
