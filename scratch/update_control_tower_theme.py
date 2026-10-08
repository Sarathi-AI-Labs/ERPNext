
target_path = r'sarathi_visibility/sarathi_visibility/public/css/sarathi_dashboard.css'
with open(target_path, encoding='utf-8') as f:
    content = f.read()

split_marker = '.sd-dashboard :is(.sd-card-icon,.sd-setup-icon) { color: var(--metric-ink); background: var(--metric-soft); border-radius: 11px; }'
parts = content.split(split_marker)
if len(parts) != 2:
    print('Error: split_marker not found exactly once!')
    exit(1)

base_css = parts[0]

# Add Google Fonts import at the very top if not already present
font_import = "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Outfit:wght@500;600;700;800;900&family=JetBrains+Mono:wght@500;600;700;800&display=swap');\n\n"
if '@import url' not in base_css:
    base_css = font_import + base_css

new_theme_css = '''/* ==========================================================================
   SARATHI CONTROL TOWER · MASTER INDUSTRIAL THEME & COLOR PALETTE
   Ultra-modern, colorful, responsive design system across all modules
   ========================================================================== */

/* 1. Global Shell & Ambient Mesh Background */
.sd-dashboard {
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  color: #0f172a !important;
  background: radial-gradient(ellipse at 12% 8%, rgba(14, 165, 233, 0.08) 0%, transparent 45%),
              radial-gradient(ellipse at 88% 18%, rgba(99, 102, 241, 0.07) 0%, transparent 45%),
              radial-gradient(ellipse at 50% 85%, rgba(16, 185, 129, 0.06) 0%, transparent 50%),
              #f8fafc !important;
  padding: 24px !important;
  border-radius: 20px !important;
  --sd-accent: #0284c7;
  --sd-accent-end: #4f46e5;
  --sd-soft: #f0f9ff;
  --sd-border: #bae6fd;
}

/* 2. Majestic Hero Header */
.sd-hero {
  position: relative;
  overflow: hidden;
  border-radius: 22px !important;
  padding: 28px 32px !important;
  background: linear-gradient(135deg, #090e17 0%, #0e2a38 35%, #0f3e50 70%, #1e1b4b 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.14) !important;
  box-shadow: 0 20px 40px -10px rgba(15, 23, 42, 0.35) !important;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 18px;
  color: white;
}
.sd-hero::before {
  content: "";
  position: absolute;
  top: -100px;
  right: -50px;
  width: 380px;
  height: 380px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(14, 165, 233, 0.25) 0%, rgba(99, 102, 241, 0.15) 50%, transparent 70%);
  pointer-events: none;
}
.sd-eyebrow {
  display: inline-block;
  font-size: 10px !important;
  letter-spacing: 2.2px !important;
  font-weight: 850 !important;
  color: #38bdf8 !important;
  background: rgba(56, 189, 248, 0.12);
  border: 1px solid rgba(56, 189, 248, 0.3);
  padding: 3px 10px;
  border-radius: 12px;
  margin-bottom: 6px;
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
  max-width: 720px;
  line-height: 1.55;
  margin: 0;
}
.sd-hero-actions {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
.sd-hero-actions [data-updated] {
  color: #94a3b8;
  font-size: 11.5px;
  font-weight: 600;
}
.sd-ai-header-btn {
  background: linear-gradient(135deg, #7c3aed 0%, #c026d3 100%) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255, 255, 255, 0.25) !important;
  box-shadow: 0 4px 14px rgba(124, 58, 237, 0.35) !important;
  font-weight: 750 !important;
}
.sd-ai-header-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(124, 58, 237, 0.45) !important;
}

/* 3. Floating Glass Filter Toolbar */
.sd-controls {
  background: rgba(255, 255, 255, 0.95) !important;
  backdrop-filter: blur(20px);
  border: 1px solid rgba(226, 232, 240, 0.9) !important;
  border-radius: 18px !important;
  padding: 18px 22px !important;
  margin: 20px 0 !important;
  box-shadow: 0 10px 30px -4px rgba(15, 23, 42, 0.05) !important;
  display: flex;
  gap: 14px;
  flex-wrap: wrap;
  align-items: flex-end;
}
.sd-controls label {
  font-size: 11px !important;
  font-weight: 800 !important;
  color: #475569 !important;
  letter-spacing: 0.6px !important;
  text-transform: uppercase;
  display: flex;
  flex-direction: column;
  gap: 5px;
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
}
.sd-date-btn-group {
  display: flex;
  align-items: center;
  gap: 8px;
  height: 40px;
}
.sd-date-btn-group .sd-primary {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 9px !important;
  font-weight: 750 !important;
  box-shadow: 0 2px 8px rgba(2, 132, 199, 0.28) !important;
}

/* 4. Multi-Colored Summary KPI Cards */
.sd-kpis {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)) !important;
  gap: 16px !important;
  margin: 20px 0 !important;
}
.sd-kpi {
  position: relative;
  background: #ffffff !important;
  border-radius: 18px !important;
  padding: 22px 24px !important;
  border: 1.5px solid #e2e8f0 !important;
  box-shadow: 0 4px 18px -2px rgba(15, 23, 42, 0.05) !important;
  transition: all 0.24s cubic-bezier(0.4, 0, 0.2, 1) !important;
  overflow: hidden;
  text-align: left;
  cursor: pointer;
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
.sd-kpi-label {
  display: flex;
  align-items: center;
  font-size: 11.5px !important;
  font-weight: 800 !important;
  text-transform: uppercase;
  letter-spacing: 0.6px !important;
  color: #475569 !important;
}
.sd-kpi-value,
.sd-kpi strong {
  font-family: 'JetBrains Mono', 'Plus Jakarta Sans', monospace !important;
  font-size: clamp(22px, 2vw, 30px) !important;
  font-weight: 850 !important;
  letter-spacing: -0.6px !important;
  color: #0f172a !important;
  margin: 10px 0 6px !important;
  display: block;
}
.sd-kpi small,
.sd-kpi-sub {
  font-size: 12px !important;
  font-weight: 550 !important;
  color: #64748b !important;
}

/* Distinctive Color Themes across all 5 KPI slots */
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

/* 5. Panels & Card Sections */
.sd-panel {
  position: relative;
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 18px !important;
  padding: 24px !important;
  margin-top: 20px !important;
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
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 12px;
  padding-bottom: 14px !important;
  margin-bottom: 16px !important;
  border-bottom: 1px solid #f1f5f9 !important;
}
.sd-panel-heading h2 {
  font-family: 'Outfit', sans-serif !important;
  font-size: 18px !important;
  font-weight: 800 !important;
  color: #0f172a !important;
  letter-spacing: -0.4px !important;
  margin: 0 0 4px !important;
}
.sd-panel-heading p {
  font-size: 13px !important;
  color: #64748b !important;
  line-height: 1.5 !important;
}

/* Card Grids */
.sd-cards {
  display: grid;
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
  cursor: pointer;
}
.sd-card:hover {
  transform: translateY(-3px) !important;
  border-color: #0284c7 !important;
  box-shadow: 0 12px 28px -4px rgba(15, 23, 42, 0.1), 0 0 16px rgba(2, 132, 199, 0.15) !important;
}
.sd-card-icon,
.sd-setup-icon {
  display: inline-grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: #f0f9ff;
  color: #0284c7;
  margin-bottom: 8px;
}

/* 6. Tabs Navigation */
.sd-tabs,
.sd-acc-tabs {
  background: #0f172a !important;
  padding: 8px 10px !important;
  border-radius: 16px !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
  display: flex !important;
  flex-wrap: wrap !important;
  gap: 6px !important;
  margin: 20px 0 !important;
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
}
.sd-tabs button:hover,
.sd-acc-tab-btn:hover {
  color: #ffffff !important;
  background: rgba(255, 255, 255, 0.1) !important;
}
.sd-tabs button.active,
.sd-acc-tab-btn.active {
  background: linear-gradient(135deg, #0284c7 0%, #4f46e5 100%) !important;
  color: #ffffff !important;
  border-color: rgba(255, 255, 255, 0.2) !important;
  box-shadow: 0 4px 16px rgba(2, 132, 199, 0.35) !important;
}

/* 7. Data Tables */
.sd-table-wrap {
  border: 1px solid #e2e8f0 !important;
  border-radius: 14px !important;
  background: #ffffff !important;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03) !important;
  overflow-x: auto;
}
.sd-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}
.sd-table th {
  background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
  color: #334155 !important;
  font-size: 11px !important;
  font-weight: 800 !important;
  letter-spacing: 0.7px !important;
  text-transform: uppercase;
  padding: 13px 16px !important;
  border-bottom: 2px solid #cbd5e1 !important;
  position: sticky;
  top: 0;
  z-index: 2;
  white-space: nowrap;
}
.sd-table td {
  padding: 13px 16px !important;
  font-size: 12.5px !important;
  color: #1e293b !important;
  border-bottom: 1px solid #f1f5f9 !important;
  vertical-align: middle;
  white-space: nowrap;
}
.sd-table tbody tr:nth-child(even) td {
  background: #fbfcfe;
}
.sd-table tbody tr:hover td {
  background: rgba(2, 132, 199, 0.05) !important;
  color: #0f172a;
}

/* Pills & Badges */
.sd-pill {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border-radius: 20px !important;
  padding: 4px 10px !important;
  font-size: 11px !important;
  font-weight: 800 !important;
  letter-spacing: 0.2px;
  white-space: nowrap;
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

/* 8. Buttons */
.sd-button {
  background: #ffffff !important;
  color: #334155 !important;
  border: 1.5px solid #cbd5e1 !important;
  padding: 8px 14px !important;
  border-radius: 9px !important;
  font-size: 12px !important;
  font-weight: 750 !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
  transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
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

/* 9. Responsive Breakpoints */
@media (max-width: 1100px) {
  .sd-kpis {
    grid-template-columns: repeat(3, 1fr) !important;
  }
}
@media (max-width: 800px) {
  .sd-dashboard {
    padding: 14px !important;
  }
  .sd-hero {
    padding: 22px 18px !important;
  }
  .sd-controls {
    flex-direction: column !important;
    align-items: stretch !important;
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
}
'''

updated_content = base_css + split_marker + '\n' + new_theme_css
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(updated_content)

print(f'Successfully updated {target_path}!')
