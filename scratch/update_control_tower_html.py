html_content = '''<div class="sod-wrapper sd-dashboard">
  <!-- Top View Switcher Bar -->
  <div class="sod-switcher-bar">
    <span class="sod-switcher-label">Dashboard View:</span>
    <button class="sod-switcher-btn" data-action="switch-owner">
      <span class="sod-switcher-icon">👑</span> Owner Executive View
    </button>
    <button class="sod-switcher-btn active" data-action="switch-pm">
      <span class="sod-switcher-icon">🏭</span> Production Operations View
    </button>
  </div>

  <div class="sod-app">
    <!-- Left Navigation Sidebar -->
    <aside class="sod-side">
      <div class="sod-brand">
        ✦ SARATHI <small>AI LABS · CONTROL TOWER</small>
      </div>
      <nav class="sod-nav sd-tabs" aria-label="Control Tower navigation"></nav>
    </aside>

    <!-- Main Content Area -->
    <main class="sod-main">
      <div class="sod-top">
        <span class="sod-breadcrumb" data-breadcrumb>Workspace /
          <a href="javascript:void(0)" class="sod-link" data-tab="overview">Control Tower</a>
          / <b id="sd-crumb-text">Operations</b></span>
        <div style="display: flex; align-items: center; gap: 12px">
          <div class="sod-live-status-pill" title="Connected to ERPNext Realtime Socket.IO Gateway">
            <span class="sod-pulse-dot"></span>
            <span data-updated>LIVE SYNCED</span>
          </div>
          <div class="sod-user-pill">
            <span id="sd-live-time"></span> &nbsp;
            <span class="sod-avatar">PM</span>
          </div>
        </div>
      </div>

      <!-- Hero Gradient Banner -->
      <section class="sod-hero sd-hero">
        <div>
          <div class="sod-eyebrow sd-eyebrow">SARATHI AI LABS · INDUSTRIAL CONTROL TOWER</div>
          <h1>Sarathi Industrial Dashboard</h1>
          <p>
            Real-time manufacturing operations, plant floor visibility, subcontracting and enterprise intelligence.
          </p>
        </div>
        <div class="sod-hero-actions sd-hero-actions">
          <button class="sod-btn sod-btn-glass sd-button" data-action="refresh" title="Sync all live values">
            ↻ Refresh
          </button>
          <button class="sod-btn sod-btn-primary sd-button sd-ai-header-btn" data-action="toggle-ai" title="Launch Sarathi AI Assistant">
            ✦ AI Agent
          </button>
        </div>
      </section>

      <!-- Global Filter Bar with Elevated Floating Glass -->
      <section class="sod-filters sd-controls" aria-label="Dashboard filters">
        <div class="sod-filter-group">
          <label>Organization</label>
          <select data-filter="company" class="sod-select" aria-label="Organization">
            <option value="">All organizations</option>
          </select>
        </div>
        <div class="sod-filter-group">
          <label>From date</label>
          <input type="date" data-date-filter="from_date" class="sod-input" aria-label="From date" />
        </div>
        <div class="sod-filter-group">
          <label>To date</label>
          <input type="date" data-date-filter="to_date" class="sod-input" aria-label="To date" />
        </div>
        <div class="sod-filter-group sod-date-btn-group sd-date-btn-group">
          <label>&nbsp;</label>
          <div style="display: flex; gap: 8px;">
            <button type="button" class="sod-btn sod-btn-primary sd-button sd-primary" data-action="apply-dates">Submit</button>
            <button type="button" class="sod-btn sod-btn-outline sd-button" data-action="clear-dates">Reset</button>
          </div>
        </div>
        <div class="sod-filter-group">
          <label>Project status</label>
          <select data-filter="status" class="sod-select" aria-label="Project status">
            <option value="">All statuses</option>
            <option>Ongoing</option>
            <option>Active</option>
            <option>Completed</option>
            <option>Delayed</option>
            <option>On hold</option>
            <option>Cancelled</option>
          </select>
        </div>
        <div class="sod-filter-group sod-search-group sd-search">
          <label>Find customers / projects</label>
          <input type="search" data-search class="sod-input" placeholder="Search by name or ID" aria-label="Find customers or projects" />
        </div>
      </section>

      <p class="sd-scope-note">
        Choose From date and To date and click Submit to filter projects by creation date, orders by order date, Work Orders by planned start, Job Cards and stock by posting date.
      </p>

      <div class="sd-error" data-error role="alert" hidden></div>
      <div class="sd-notice" data-permissions hidden></div>

      <!-- Summary KPI Cards Strip -->
      <section class="sd-kpis" data-kpis aria-label="Summary"></section>

      <!-- Live project production -->
      <section data-live-projects aria-label="Live project production"></section>

      <!-- Subcontracting Operations Panel -->
      <section class="sod-panel sd-panel" data-subcontracting-card-panel>
        <div class="sd-panel-heading">
          <div>
            <h2>Subcontracting Operations</h2>
            <p>Outsourced manufacturing, supplier materials and tracking</p>
          </div>
          <span class="sod-pill sod-pill-blue sd-pill sd-status-blue">Subcontracting</span>
        </div>
        <div class="sd-cards" data-subcontracting-cards></div>
      </section>

      <!-- Finance & Accounting Panel -->
      <section class="sod-panel sd-panel" data-accounting-card-panel>
        <div class="sd-panel-heading">
          <div>
            <h2>Finance & Accounting</h2>
            <p>Executive financial intelligence, cash liquidity, profitability & GL traceability</p>
          </div>
          <span class="sod-pill sod-pill-green sd-pill sd-status-green">Accounting Intelligence</span>
        </div>
        <div class="sd-cards" data-accounting-cards></div>
      </section>

      <!-- Customers Panel -->
      <section class="sod-panel sd-panel" data-customer-panel>
        <div class="sd-panel-heading">
          <div>
            <h2>Customers</h2>
            <p>Choose a customer to focus every chart and report</p>
          </div>
          <button class="sod-btn sod-btn-sm sod-btn-outline sd-button" data-action="associate">
            Link existing customer
          </button>
        </div>
        <div class="sd-cards" data-customers></div>
        <div data-customer-pagination></div>
      </section>

      <!-- Projects Panel -->
      <section class="sod-panel sd-panel" data-project-panel>
        <div class="sd-panel-heading">
          <div>
            <h2 data-project-heading>Organization projects</h2>
            <p>Choose a project to inspect its manufacturing records</p>
          </div>
          <span class="sod-pill sod-pill-amber sd-pill" data-project-count></span>
        </div>
        <div class="sd-cards" data-projects></div>
        <div data-project-pagination></div>
      </section>

      <!-- Project Summary -->
      <section class="sd-project-summary" data-project-summary hidden></section>
      <section data-subcontracting-view hidden aria-label="Subcontracting Detail View"></section>
      <section data-accounting-view hidden aria-label="Accounting Detail View"></section>

      <!-- Content Area for Selected Tab -->
      <section data-content role="tabpanel" class="sd-tab-content-panel"></section>

      <footer class="sd-footer">
        Live ERPNext records · Refreshes every 30 seconds while this page is visible · Shared stock is availability, not a project allocation
      </footer>
    </main>
  </div>
</div>
'''

target_path = r'sarathi_visibility/sarathi_visibility/sarathi_visibility/page/sarathicontroltower/sarathicontroltower.html'
with open(target_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Updated {target_path} successfully!")
