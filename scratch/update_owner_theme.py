
target_path = r'sarathi_owner/sarathi_owner/public/css/sarathi_owner_dashboard.css'
with open(target_path, encoding='utf-8') as f:
    content = f.read()

split_marker = '/* Executive workspace theme. Pipeline sections deliberately retain their original styles. */'
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
   SARATHI OWNER TOWER · MASTER EXECUTIVE THEME & COLOR PALETTE
   Ultra-modern, colorful, responsive design system across all 17 sidebar sections
   ========================================================================== */

/* 1. Global Shell & Ambient Mesh Background */
.sod-wrapper {
  font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
  color: #0f172a;
  background: radial-gradient(ellipse at 12% 8%, rgba(99, 102, 241, 0.08) 0%, transparent 45%),
              radial-gradient(ellipse at 88% 18%, rgba(14, 165, 233, 0.07) 0%, transparent 45%),
              radial-gradient(ellipse at 50% 85%, rgba(168, 85, 247, 0.06) 0%, transparent 50%),
              #f8fafc !important;
  min-height: 100vh;
  --workspace-accent: #6366f1;
  --workspace-end: #3b82f6;
  --workspace-soft: #eef2ff;
  --workspace-border: #c7d2fe;
  --workspace-glow: rgba(99, 102, 241, 0.35);
}

/* Workspace Dynamic Accents */
.sod-wrapper[data-workspace="home"] {
  --workspace-accent: #6366f1;
  --workspace-end: #8b5cf6;
  --workspace-soft: #eef2ff;
  --workspace-border: #c7d2fe;
  --workspace-glow: rgba(99, 102, 241, 0.35);
}
.sod-wrapper[data-workspace="projects"] {
  --workspace-accent: #2563eb;
  --workspace-end: #0284c7;
  --workspace-soft: #eff6ff;
  --workspace-border: #bfdbfe;
  --workspace-glow: rgba(37, 99, 235, 0.35);
}
.sod-wrapper[data-workspace="project_detail"] {
  --workspace-accent: #0891b2;
  --workspace-end: #06b6d4;
  --workspace-soft: #ecfeff;
  --workspace-border: #a5f3fc;
  --workspace-glow: rgba(8, 145, 178, 0.35);
}
.sod-wrapper[data-workspace="customers"] {
  --workspace-accent: #059669;
  --workspace-end: #10b981;
  --workspace-soft: #ecfdf5;
  --workspace-border: #a7f3d0;
  --workspace-glow: rgba(5, 150, 105, 0.35);
}
.sod-wrapper[data-workspace="sales_orders"] {
  --workspace-accent: #d97706;
  --workspace-end: #f59e0b;
  --workspace-soft: #fffbeb;
  --workspace-border: #fde68a;
  --workspace-glow: rgba(217, 119, 6, 0.35);
}
.sod-wrapper[data-workspace="manufacturing"] {
  --workspace-accent: #ea580c;
  --workspace-end: #f97316;
  --workspace-soft: #fff7ed;
  --workspace-border: #fed7aa;
  --workspace-glow: rgba(234, 88, 12, 0.35);
}
.sod-wrapper[data-workspace="stock_quality"] {
  --workspace-accent: #65a30d;
  --workspace-end: #84cc16;
  --workspace-soft: #f7fee7;
  --workspace-border: #d9f99d;
  --workspace-glow: rgba(101, 163, 13, 0.35);
}
.sod-wrapper[data-workspace="invoicing"] {
  --workspace-accent: #c026d3;
  --workspace-end: #d946ef;
  --workspace-soft: #fdf4ff;
  --workspace-border: #f5d0fe;
  --workspace-glow: rgba(192, 38, 211, 0.35);
}
.sod-wrapper[data-workspace="payments"] {
  --workspace-accent: #7c3aed;
  --workspace-end: #8b5cf6;
  --workspace-soft: #f5f3ff;
  --workspace-border: #ddd6fe;
  --workspace-glow: rgba(124, 58, 237, 0.35);
}
.sod-wrapper[data-workspace="financial_reports"] {
  --workspace-accent: #9333ea;
  --workspace-end: #a855f7;
  --workspace-soft: #faf5ff;
  --workspace-border: #e9d5ff;
  --workspace-glow: rgba(147, 51, 234, 0.35);
}
.sod-wrapper[data-workspace="accounts_setup"] {
  --workspace-accent: #e11d48;
  --workspace-end: #fb7185;
  --workspace-soft: #fff1f2;
  --workspace-border: #fecdd3;
  --workspace-glow: rgba(225, 29, 72, 0.35);
}
.sod-wrapper[data-workspace="taxes"] {
  --workspace-accent: #dc2626;
  --workspace-end: #ef4444;
  --workspace-soft: #fef2f2;
  --workspace-border: #fecaca;
  --workspace-glow: rgba(220, 38, 38, 0.35);
}
.sod-wrapper[data-workspace="banking"] {
  --workspace-accent: #0f766e;
  --workspace-end: #14b8a6;
  --workspace-soft: #f0fdfa;
  --workspace-border: #99f6e4;
  --workspace-glow: rgba(15, 118, 110, 0.35);
}
.sod-wrapper[data-workspace="budget"] {
  --workspace-accent: #ca8a04;
  --workspace-end: #eab308;
  --workspace-soft: #fefce8;
  --workspace-border: #fef08a;
  --workspace-glow: rgba(202, 138, 4, 0.35);
}
.sod-wrapper[data-workspace="share_management"] {
  --workspace-accent: #4338ca;
  --workspace-end: #6366f1;
  --workspace-soft: #eef2ff;
  --workspace-border: #c7d2fe;
  --workspace-glow: rgba(67, 56, 202, 0.35);
}
.sod-wrapper[data-workspace="subscription"] {
  --workspace-accent: #0284c7;
  --workspace-end: #38bdf8;
  --workspace-soft: #f0f9ff;
  --workspace-border: #bae6fd;
  --workspace-glow: rgba(2, 132, 199, 0.35);
}
.sod-wrapper[data-workspace="reports"] {
  --workspace-accent: #0d9488;
  --workspace-end: #10b981;
  --workspace-soft: #f0fdfa;
  --workspace-border: #99f6e4;
  --workspace-glow: rgba(13, 148, 136, 0.35);
}

/* 2. Top View Switcher Bar */
.sod-switcher-bar {
  background: rgba(11, 17, 32, 0.96) !important;
  backdrop-filter: blur(16px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  padding: 8px 24px !important;
  min-height: 48px !important;
  display: flex;
  align-items: center;
  gap: 14px;
}
.sod-switcher-label {
  color: #94a3b8 !important;
  font-size: 11px !important;
  font-weight: 800 !important;
  letter-spacing: 1.4px !important;
}
.sod-switcher-btn {
  background: rgba(255, 255, 255, 0.08) !important;
  border: 1px solid rgba(255, 255, 255, 0.15) !important;
  color: #e2e8f0 !important;
  padding: 6px 14px !important;
  border-radius: 20px !important;
  font-size: 12px !important;
  font-weight: 700 !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.sod-switcher-btn:hover {
  background: rgba(255, 255, 255, 0.16) !important;
  color: #ffffff !important;
  transform: translateY(-1px);
}
.sod-switcher-btn.active[data-action="switch-owner"] {
  background: linear-gradient(135deg, #d97706 0%, #b45309 100%) !important;
  border-color: #f59e0b !important;
  color: #ffffff !important;
  box-shadow: 0 4px 18px rgba(245, 158, 11, 0.35) !important;
}
.sod-switcher-btn.active[data-action="switch-pm"] {
  background: linear-gradient(135deg, #059669 0%, #0d9488 100%) !important;
  border-color: #10b981 !important;
  color: #ffffff !important;
  box-shadow: 0 4px 18px rgba(16, 185, 129, 0.35) !important;
}

/* 3. Sleek Sticky Sidebar */
.sod-side {
  background: linear-gradient(180deg, #0b1120 0%, #0f172a 50%, #1e1b4b 100%) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.08) !important;
  padding: 20px 12px 30px !important;
  box-shadow: 4px 0 24px rgba(0, 0, 0, 0.25);
}
.sod-brand {
  padding: 8px 10px 18px !important;
  margin-bottom: 14px !important;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
  font-family: 'Outfit', sans-serif !important;
  font-size: 20px !important;
  font-weight: 850 !important;
  letter-spacing: 1.5px !important;
  background: linear-gradient(135deg, #ffffff 0%, #c7d2fe 50%, #38bdf8 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
.sod-brand small {
  display: block;
  font-family: 'Plus Jakarta Sans', sans-serif !important;
  font-size: 9.5px !important;
  font-weight: 800 !important;
  letter-spacing: 2px !important;
  color: #94a3b8 !important;
  margin-top: 5px !important;
  -webkit-text-fill-color: #94a3b8;
}

/* Section Category Badges */
.sod-nav-section-title {
  color: #94a3b8 !important;
  font-size: 9.5px !important;
  font-weight: 850 !important;
  letter-spacing: 1.6px !important;
  text-transform: uppercase;
  margin: 14px 6px 6px !important;
  padding-top: 10px !important;
  border-top: 1px solid rgba(255, 255, 255, 0.08) !important;
  display: flex;
  align-items: center;
  gap: 6px;
}
.sod-nav-section-title:first-child {
  border-top: none !important;
  margin-top: 2px !important;
  padding-top: 0 !important;
}

/* Individual Color Combinations for Every Sidebar Nav Item */
.sod-nav button {
  position: relative;
  width: 100%;
  display: flex;
  align-items: center;
  gap: 11px;
  border-radius: 11px !important;
  padding: 10px 12px !important;
  margin: 2px 0 !important;
  color: #cbd5e1 !important;
  font-size: 13px !important;
  font-weight: 600 !important;
  background: transparent !important;
  border: 1px solid transparent !important;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.sod-nav button .sod-icon {
  display: inline-grid;
  place-items: center;
  width: 32px !important;
  min-width: 32px !important;
  height: 32px !important;
  border-radius: 9px !important;
  background: var(--nav-icon-bg, rgba(255, 255, 255, 0.08)) !important;
  color: var(--nav-icon-color, #94a3b8) !important;
  transition: all 0.2s ease !important;
}

.sod-nav button:hover {
  background: var(--nav-hover-bg, rgba(255, 255, 255, 0.08)) !important;
  color: #ffffff !important;
  transform: translateX(4px);
  border-color: rgba(255, 255, 255, 0.08) !important;
}

.sod-nav button:hover .sod-icon {
  transform: scale(1.08);
  box-shadow: 0 0 14px var(--nav-glow, rgba(255, 255, 255, 0.2));
}

.sod-nav button.active {
  background: var(--nav-active-bg, linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%)) !important;
  color: #ffffff !important;
  font-weight: 750 !important;
  box-shadow: 0 6px 20px var(--nav-glow, rgba(79, 70, 229, 0.4)), inset 3.5px 0 0 var(--nav-active-border, #ffffff) !important;
}

.sod-nav button.active .sod-icon {
  background: rgba(255, 255, 255, 0.25) !important;
  color: #ffffff !important;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
}

/* 1. Owner Home */
.sod-nav button[data-key="home"] {
  --nav-icon-bg: rgba(99, 102, 241, 0.16);
  --nav-icon-color: #a5b4fc;
  --nav-hover-bg: rgba(99, 102, 241, 0.12);
  --nav-active-bg: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  --nav-active-border: #c7d2fe;
  --nav-glow: rgba(99, 102, 241, 0.45);
}

/* 2. Projects */
.sod-nav button[data-key="projects"] {
  --nav-icon-bg: rgba(37, 99, 235, 0.16);
  --nav-icon-color: #93c5fd;
  --nav-hover-bg: rgba(37, 99, 235, 0.12);
  --nav-active-bg: linear-gradient(135deg, #2563eb 0%, #0284c7 100%);
  --nav-active-border: #bfdbfe;
  --nav-glow: rgba(37, 99, 235, 0.45);
}

/* 3. Project Detail */
.sod-nav button[data-key="project_detail"] {
  --nav-icon-bg: rgba(8, 145, 178, 0.16);
  --nav-icon-color: #67e8f9;
  --nav-hover-bg: rgba(8, 145, 178, 0.12);
  --nav-active-bg: linear-gradient(135deg, #0891b2 0%, #06b6d4 100%);
  --nav-active-border: #a5f3fc;
  --nav-glow: rgba(8, 145, 178, 0.45);
}

/* 4. Customers */
.sod-nav button[data-key="customers"] {
  --nav-icon-bg: rgba(16, 185, 129, 0.16);
  --nav-icon-color: #6ee7b7;
  --nav-hover-bg: rgba(16, 185, 129, 0.12);
  --nav-active-bg: linear-gradient(135deg, #059669 0%, #10b981 100%);
  --nav-active-border: #a7f3d0;
  --nav-glow: rgba(16, 185, 129, 0.45);
}

/* 5. Sales Orders */
.sod-nav button[data-key="sales_orders"] {
  --nav-icon-bg: rgba(245, 158, 11, 0.16);
  --nav-icon-color: #fcd34d;
  --nav-hover-bg: rgba(245, 158, 11, 0.12);
  --nav-active-bg: linear-gradient(135deg, #d97706 0%, #f59e0b 100%);
  --nav-active-border: #fde68a;
  --nav-glow: rgba(245, 158, 11, 0.45);
}

/* 6. Manufacturing */
.sod-nav button[data-key="manufacturing"] {
  --nav-icon-bg: rgba(249, 115, 22, 0.16);
  --nav-icon-color: #fdba74;
  --nav-hover-bg: rgba(249, 115, 22, 0.12);
  --nav-active-bg: linear-gradient(135deg, #ea580c 0%, #f97316 100%);
  --nav-active-border: #fed7aa;
  --nav-glow: rgba(249, 115, 22, 0.45);
}

/* 7. Working Capital & Stock */
.sod-nav button[data-key="stock_quality"] {
  --nav-icon-bg: rgba(132, 204, 22, 0.16);
  --nav-icon-color: #bef264;
  --nav-hover-bg: rgba(132, 204, 22, 0.12);
  --nav-active-bg: linear-gradient(135deg, #65a30d 0%, #84cc16 100%);
  --nav-active-border: #d9f99d;
  --nav-glow: rgba(132, 204, 22, 0.45);
}

/* 8. Invoicing */
.sod-nav button[data-key="invoicing"] {
  --nav-icon-bg: rgba(217, 70, 239, 0.16);
  --nav-icon-color: #f0abfc;
  --nav-hover-bg: rgba(217, 70, 239, 0.12);
  --nav-active-bg: linear-gradient(135deg, #c026d3 0%, #d946ef 100%);
  --nav-active-border: #f5d0fe;
  --nav-glow: rgba(217, 70, 239, 0.45);
}

/* 9. Payments */
.sod-nav button[data-key="payments"] {
  --nav-icon-bg: rgba(124, 58, 237, 0.16);
  --nav-icon-color: #c4b5fd;
  --nav-hover-bg: rgba(124, 58, 237, 0.12);
  --nav-active-bg: linear-gradient(135deg, #7c3aed 0%, #8b5cf6 100%);
  --nav-active-border: #ddd6fe;
  --nav-glow: rgba(124, 58, 237, 0.45);
}

/* 10. Financial Reports */
.sod-nav button[data-key="financial_reports"] {
  --nav-icon-bg: rgba(147, 51, 234, 0.16);
  --nav-icon-color: #d8b4fe;
  --nav-hover-bg: rgba(147, 51, 234, 0.12);
  --nav-active-bg: linear-gradient(135deg, #9333ea 0%, #a855f7 100%);
  --nav-active-border: #e9d5ff;
  --nav-glow: rgba(147, 51, 234, 0.45);
}

/* 11. Accounts Setup */
.sod-nav button[data-key="accounts_setup"] {
  --nav-icon-bg: rgba(225, 29, 72, 0.16);
  --nav-icon-color: #fda4af;
  --nav-hover-bg: rgba(225, 29, 72, 0.12);
  --nav-active-bg: linear-gradient(135deg, #e11d48 0%, #fb7185 100%);
  --nav-active-border: #fecdd3;
  --nav-glow: rgba(225, 29, 72, 0.45);
}

/* 12. Taxes */
.sod-nav button[data-key="taxes"] {
  --nav-icon-bg: rgba(239, 68, 68, 0.16);
  --nav-icon-color: #fca5a5;
  --nav-hover-bg: rgba(239, 68, 68, 0.12);
  --nav-active-bg: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
  --nav-active-border: #fecaca;
  --nav-glow: rgba(239, 68, 68, 0.45);
}

/* 13. Banking */
.sod-nav button[data-key="banking"] {
  --nav-icon-bg: rgba(15, 118, 110, 0.16);
  --nav-icon-color: #5eead4;
  --nav-hover-bg: rgba(15, 118, 110, 0.12);
  --nav-active-bg: linear-gradient(135deg, #0f766e 0%, #14b8a6 100%);
  --nav-active-border: #99f6e4;
  --nav-glow: rgba(15, 118, 110, 0.45);
}

/* 14. Budget */
.sod-nav button[data-key="budget"] {
  --nav-icon-bg: rgba(202, 138, 4, 0.16);
  --nav-icon-color: #fde047;
  --nav-hover-bg: rgba(202, 138, 4, 0.12);
  --nav-active-bg: linear-gradient(135deg, #ca8a04 0%, #eab308 100%);
  --nav-active-border: #fef08a;
  --nav-glow: rgba(202, 138, 4, 0.45);
}

/* 15. Share Management */
.sod-nav button[data-key="share_management"] {
  --nav-icon-bg: rgba(67, 56, 202, 0.16);
  --nav-icon-color: #a5b4fc;
  --nav-hover-bg: rgba(67, 56, 202, 0.12);
  --nav-active-bg: linear-gradient(135deg, #4338ca 0%, #6366f1 100%);
  --nav-active-border: #c7d2fe;
  --nav-glow: rgba(67, 56, 202, 0.45);
}

/* 16. Subscription */
.sod-nav button[data-key="subscription"] {
  --nav-icon-bg: rgba(2, 132, 199, 0.16);
  --nav-icon-color: #7dd3fc;
  --nav-hover-bg: rgba(2, 132, 199, 0.12);
  --nav-active-bg: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
  --nav-active-border: #bae6fd;
  --nav-glow: rgba(2, 132, 199, 0.45);
}

/* 17. Executive Decision Reports */
.sod-nav button[data-key="reports"] {
  --nav-icon-bg: rgba(13, 148, 136, 0.16);
  --nav-icon-color: #5eead4;
  --nav-hover-bg: rgba(13, 148, 136, 0.12);
  --nav-active-bg: linear-gradient(135deg, #0d9488 0%, #10b981 100%);
  --nav-active-border: #99f6e4;
  --nav-glow: rgba(13, 148, 136, 0.45);
}

/* Accounting & Finance Accordion */
.sod-nav-dropdown-group {
  margin: 10px 0 !important;
  border-radius: 12px !important;
  border: 1px solid rgba(255, 255, 255, 0.12) !important;
  background: rgba(15, 23, 42, 0.5) !important;
  overflow: hidden;
}
.sod-nav-dropdown-toggle {
  padding: 10px 12px !important;
  color: #e2e8f0 !important;
  font-weight: 800 !important;
  letter-spacing: 0.8px !important;
}
.sod-nav-dropdown-badge {
  background: linear-gradient(135deg, #059669, #10b981) !important;
  color: #ffffff !important;
  padding: 3px 8px !important;
  border-radius: 10px !important;
  font-weight: 850 !important;
  box-shadow: 0 2px 6px rgba(16, 185, 129, 0.3);
}

/* 4. Top Header & Breadcrumb */
.sod-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 18px !important;
  padding: 4px 2px !important;
}
.sod-breadcrumb {
  font-size: 13px !important;
  color: #64748b !important;
  font-weight: 600;
}
.sod-breadcrumb b {
  color: #0f172a !important;
  font-weight: 800 !important;
}
.sod-live-status-pill {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  background: #ecfdf5 !important;
  border: 1.5px solid #a7f3d0 !important;
  color: #065f46 !important;
  font-size: 11px !important;
  font-weight: 800 !important;
  padding: 4px 12px !important;
  border-radius: 20px !important;
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.15) !important;
}
.sod-pulse-dot {
  width: 8px !important;
  height: 8px !important;
  background-color: #10b981 !important;
  border-radius: 50% !important;
  display: inline-block;
  box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  animation: sodPulse 1.8s infinite !important;
}
.sod-avatar {
  background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
  color: #ffffff !important;
  border: 2px solid #ffffff !important;
  box-shadow: 0 2px 10px rgba(99, 102, 241, 0.3) !important;
  width: 38px !important;
  height: 38px !important;
  font-weight: 850 !important;
}

/* 5. Majestic Hero Banner */
.sod-hero {
  position: relative;
  overflow: hidden;
  border-radius: 22px !important;
  padding: 28px 32px !important;
  background: linear-gradient(135deg, #090e17 0%, #151d38 35%, #1e295d 70%, #0c4a6e 100%) !important;
  border: 1px solid rgba(255, 255, 255, 0.14) !important;
  box-shadow: 0 20px 40px -10px rgba(15, 23, 42, 0.35) !important;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 18px;
  color: white;
}
.sod-hero::before {
  content: "";
  position: absolute;
  top: -100px;
  right: -50px;
  width: 380px;
  height: 380px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, rgba(14, 165, 233, 0.15) 50%, transparent 70%);
  pointer-events: none;
}
.sod-eyebrow {
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
.sod-hero h1 {
  font-family: 'Outfit', sans-serif !important;
  font-size: clamp(26px, 2.5vw, 36px) !important;
  font-weight: 850 !important;
  letter-spacing: -0.6px !important;
  margin: 6px 0 !important;
  color: #ffffff !important;
}
.sod-hero p {
  color: #cbd5e1 !important;
  font-size: 14px !important;
  max-width: 720px;
  line-height: 1.55;
  margin: 0;
}
.sod-btn-glass {
  background: rgba(255, 255, 255, 0.14) !important;
  backdrop-filter: blur(12px);
  border: 1.5px solid rgba(255, 255, 255, 0.28) !important;
  color: #ffffff !important;
  padding: 9px 18px !important;
  border-radius: 12px !important;
  font-size: 12.5px !important;
  font-weight: 750 !important;
  box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2) !important;
  transition: all 0.2s ease !important;
}
.sod-btn-glass:hover {
  background: rgba(255, 255, 255, 0.25) !important;
  transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.3) !important;
}

/* 6. Floating Glass Filter Controls */
.sod-filters {
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
.sod-filter-group label {
  font-size: 11px !important;
  font-weight: 800 !important;
  color: #475569 !important;
  letter-spacing: 0.6px !important;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  gap: 5px;
}
.sod-filter-group label::before {
  content: "";
  display: inline-block;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--workspace-accent, #6366f1);
}
.sod-select,
.sod-input,
.sod-combo-input {
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
.sod-combo-input:hover {
  background: #ffffff !important;
  border-color: #94a3b8 !important;
}
.sod-select:focus,
.sod-input:focus,
.sod-combo-input:focus {
  background: #ffffff !important;
  border-color: var(--workspace-accent, #6366f1) !important;
  box-shadow: 0 0 0 3.5px var(--workspace-soft, rgba(99, 102, 241, 0.16)) !important;
}
.sod-suggestions-menu {
  border-radius: 14px !important;
  border: 1px solid #cbd5e1 !important;
  box-shadow: 0 16px 36px -6px rgba(15, 23, 42, 0.15) !important;
  padding: 6px !important;
  background: #ffffff !important;
}
.sod-suggestion-item {
  border-radius: 8px !important;
  padding: 9px 12px !important;
  font-weight: 600 !important;
}
.sod-suggestion-item:hover,
.sod-suggestion-item.selected {
  background: #f1f5f9 !important;
  color: var(--workspace-accent, #4f46e5) !important;
}

/* Floating Date Picker Popover */
.sod-date-popover {
  background: #ffffff !important;
  border: 1.5px solid #cbd5e1 !important;
  border-radius: 16px !important;
  box-shadow: 0 20px 40px -8px rgba(15, 23, 42, 0.22) !important;
}
.sod-btn-date-apply {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
  color: #ffffff !important;
  border-radius: 9px !important;
  font-weight: 750 !important;
  box-shadow: 0 3px 10px rgba(79, 70, 229, 0.3) !important;
}

/* 7. Multi-Colored Executive KPI Cards */
.sod-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)) !important;
  gap: 16px !important;
}
.sod-card {
  position: relative;
  background: #ffffff !important;
  border-radius: 18px !important;
  padding: 22px 24px !important;
  border: 1.5px solid #e2e8f0 !important;
  box-shadow: 0 4px 18px -2px rgba(15, 23, 42, 0.05) !important;
  transition: all 0.24s cubic-bezier(0.4, 0, 0.2, 1) !important;
  overflow: hidden;
}
.sod-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4.5px;
  background: var(--card-accent, linear-gradient(90deg, #6366f1, #8b5cf6));
  border-radius: 18px 18px 0 0;
}
.sod-card:hover {
  transform: translateY(-4px) !important;
  border-color: var(--card-border, #818cf8) !important;
  box-shadow: 0 18px 36px -6px rgba(15, 23, 42, 0.12), 0 0 24px var(--card-glow, rgba(99, 102, 241, 0.15)) !important;
}
.sod-card .sod-label {
  display: flex;
  align-items: center;
  font-size: 11.5px !important;
  font-weight: 800 !important;
  text-transform: uppercase;
  letter-spacing: 0.6px !important;
  color: #475569 !important;
}
.sod-card strong {
  font-family: 'JetBrains Mono', 'Plus Jakarta Sans', monospace !important;
  font-size: clamp(22px, 2vw, 30px) !important;
  font-weight: 850 !important;
  letter-spacing: -0.6px !important;
  color: #0f172a !important;
  margin: 10px 0 6px !important;
  display: block;
}
.sod-card small {
  font-size: 12px !important;
  font-weight: 550 !important;
  color: #64748b !important;
}
.sod-card .sod-metric-icon {
  display: inline-grid;
  place-items: center;
  width: 34px !important;
  height: 34px !important;
  border-radius: 10px !important;
  background: var(--card-soft, #f1f5f9) !important;
  color: var(--card-primary, #475569) !important;
  margin-right: 9px !important;
  flex-shrink: 0;
}

/* Distinctive Color Themes across all 5 KPI slots */
.sod-cards > .sod-card:nth-child(5n+1),
.sod-card.blue {
  --card-accent: linear-gradient(90deg, #2563eb, #38bdf8);
  --card-border: #93c5fd;
  --card-primary: #1d4ed8;
  --card-soft: #eff6ff;
  --card-glow: rgba(37, 99, 235, 0.2);
}
.sod-cards > .sod-card:nth-child(5n+2),
.sod-card.green {
  --card-accent: linear-gradient(90deg, #059669, #10b981);
  --card-border: #6ee7b7;
  --card-primary: #047857;
  --card-soft: #ecfdf5;
  --card-glow: rgba(16, 185, 129, 0.2);
}
.sod-cards > .sod-card:nth-child(5n+3),
.sod-card.amber {
  --card-accent: linear-gradient(90deg, #d97706, #f59e0b);
  --card-border: #fcd34d;
  --card-primary: #b45309;
  --card-soft: #fffbeb;
  --card-glow: rgba(245, 158, 11, 0.2);
}
.sod-cards > .sod-card:nth-child(5n+4),
.sod-card.purple {
  --card-accent: linear-gradient(90deg, #7c3aed, #d946ef);
  --card-border: #c4b5fd;
  --card-primary: #6d28d9;
  --card-soft: #faf5ff;
  --card-glow: rgba(124, 58, 237, 0.2);
}
.sod-cards > .sod-card:nth-child(5n+5),
.sod-card.cyan,
.sod-card.red {
  --card-accent: linear-gradient(90deg, #e11d48, #f43f5e);
  --card-border: #fda4af;
  --card-primary: #be123c;
  --card-soft: #fff1f2;
  --card-glow: rgba(225, 29, 72, 0.2);
}

/* 8. Panels, Headings & Visual Structure */
.sod-panel {
  position: relative;
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 18px !important;
  padding: 24px !important;
  margin-top: 20px !important;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05) !important;
}
.sod-panel::before {
  content: "";
  position: absolute;
  top: 0;
  left: 24px;
  right: 24px;
  height: 3px;
  background: linear-gradient(90deg, var(--workspace-accent, #6366f1) 0%, var(--workspace-end, #06b6d4) 100%);
  border-radius: 0 0 3px 3px;
}
.sod-panel-head {
  padding-bottom: 14px !important;
  margin-bottom: 16px !important;
  border-bottom: 1px solid #f1f5f9 !important;
}
.sod-panel-head h2,
.sod-panel h2 {
  font-family: 'Outfit', sans-serif !important;
  font-size: 18px !important;
  font-weight: 800 !important;
  color: #0f172a !important;
  letter-spacing: -0.4px !important;
  margin: 0 0 4px !important;
}
.sod-panel-head p,
.sod-panel p {
  font-size: 13px !important;
  color: #64748b !important;
  line-height: 1.5 !important;
}

/* 9. Data Tables & Grids */
.sod-tablewrap {
  border: 1px solid #e2e8f0 !important;
  border-radius: 14px !important;
  background: #ffffff !important;
  box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03) !important;
  overflow-x: auto;
}
.sod-table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}
.sod-table th {
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
.sod-table td {
  padding: 13px 16px !important;
  font-size: 12.5px !important;
  color: #1e293b !important;
  border-bottom: 1px solid #f1f5f9 !important;
  vertical-align: middle;
  white-space: nowrap;
}
.sod-table tbody tr:nth-child(even) td {
  background: #fbfcfe;
}
.sod-table tbody tr:hover td {
  background: rgba(99, 102, 241, 0.05) !important;
  color: #0f172a;
}

/* Status Badges */
.sod-pill {
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
.sod-pill.green {
  background: #ecfdf5 !important;
  color: #065f46 !important;
  border: 1px solid #a7f3d0 !important;
  box-shadow: 0 1px 3px rgba(16, 185, 129, 0.12) !important;
}
.sod-pill.blue {
  background: #eff6ff !important;
  color: #1e40af !important;
  border: 1px solid #bfdbfe !important;
  box-shadow: 0 1px 3px rgba(37, 99, 235, 0.12) !important;
}
.sod-pill.amber,
.sod-pill.orange {
  background: #fffbeb !important;
  color: #92400e !important;
  border: 1px solid #fde68a !important;
  box-shadow: 0 1px 3px rgba(245, 158, 11, 0.12) !important;
}
.sod-pill.red {
  background: #fef2f2 !important;
  color: #991b1b !important;
  border: 1px solid #fecaca !important;
  box-shadow: 0 1px 3px rgba(239, 68, 68, 0.12) !important;
}
.sod-pill.purple {
  background: #faf5ff !important;
  color: #6b21a8 !important;
  border: 1px solid #e9d5ff !important;
  box-shadow: 0 1px 3px rgba(147, 51, 234, 0.12) !important;
}

/* 10. Buttons & Interactive Links */
.sod-btn-sm {
  background: #ffffff !important;
  color: #334155 !important;
  border: 1.5px solid #cbd5e1 !important;
  padding: 7px 14px !important;
  border-radius: 9px !important;
  font-size: 12px !important;
  font-weight: 750 !important;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04) !important;
  transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.sod-btn-sm:hover {
  background: #f8fafc !important;
  color: var(--workspace-accent, #4f46e5) !important;
  border-color: var(--workspace-accent, #6366f1) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.18) !important;
}
.sod-link {
  color: var(--workspace-accent, #4f46e5) !important;
  font-weight: 750 !important;
  text-decoration: none !important;
}
.sod-link:hover {
  text-decoration: underline !important;
}

/* 11. Interactive Chart Cards */
.sod-chart-card {
  position: relative;
  background: #ffffff !important;
  border: 1px solid #e2e8f0 !important;
  border-radius: 18px !important;
  padding: 22px 24px !important;
  box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05) !important;
  margin-bottom: 20px !important;
}
.sod-chart-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 24px;
  right: 24px;
  height: 3px;
  background: linear-gradient(90deg, #6366f1 0%, #06b6d4 100%);
  border-radius: 0 0 3px 3px;
}
.sod-chart-card-head h2 {
  font-family: 'Outfit', sans-serif !important;
  font-size: 16px !important;
  font-weight: 800 !important;
  color: #0f172a !important;
}

/* 12. Modal & Dialog Overlays */
.sod-modal-backdrop {
  background: rgba(15, 23, 42, 0.65) !important;
  backdrop-filter: blur(8px);
}
.sod-modal {
  border-radius: 20px !important;
  border: 1px solid #cbd5e1 !important;
  box-shadow: 0 25px 50px -12px rgba(15, 23, 42, 0.35) !important;
}

/* 13. Flawless Responsive Breakpoints */
@media (max-width: 1200px) {
  .sod-cards {
    grid-template-columns: repeat(3, 1fr) !important;
  }
}
@media (max-width: 900px) {
  .sod-cards {
    grid-template-columns: repeat(2, 1fr) !important;
  }
}
@media (max-width: 820px) {
  .sod-app {
    display: flex !important;
    flex-direction: column !important;
  }
  .sod-side {
    position: relative !important;
    height: auto !important;
    max-height: none !important;
    width: 100% !important;
    padding: 12px 14px !important;
  }
  .sod-nav {
    display: flex !important;
    flex-direction: row !important;
    overflow-x: auto !important;
    padding-bottom: 8px !important;
    gap: 8px !important;
  }
  .sod-nav button {
    flex-shrink: 0 !important;
    width: auto !important;
  }
  .sod-nav-section-title {
    display: none !important;
  }
  .sod-main {
    padding: 16px 14px 60px !important;
  }
}
@media (max-width: 480px) {
  .sod-cards {
    grid-template-columns: 1fr !important;
  }
  .sod-hero {
    padding: 20px 16px !important;
  }
  .sod-filters {
    padding: 14px !important;
  }
}
'''

updated_content = base_css + split_marker + '\n' + new_theme_css
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(updated_content)

print(f'Successfully updated {target_path}!')
