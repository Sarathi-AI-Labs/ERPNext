/* Sarathi Owner Dashboard - Frontend Controller
   Live Reports, Interactive Frappe Charts, Real-Time Socket.IO Updates, and Live Changing Values.
*/

frappe.provide("frappe.SarathiOwnerDashboard");

frappe.SarathiOwnerDashboard = class {
	workspaceIcon(label = "") {
		const text = String(label).toLowerCase();
		const shapes = [
			[
				/customer|supplier|share|people/,
				'<circle cx="9" cy="8" r="3"/><path d="M3 21v-3a6 6 0 0 1 12 0v3M16 5a3 3 0 0 1 0 6m2 4a5 5 0 0 1 3 4v2"/>',
			],
			[
				/stock|material|warehouse|inventory|item/,
				'<path d="m12 3 9 5v9l-9 5-9-5V8l9-5Zm0 9 9-4M12 12 3 8m9 4v10M7 5.8l9 5"/>',
			],
			[
				/manufactur|production|operation|work order|workstation|job card|subcontract/,
				'<path d="M3 21V10l6 3V8l6 3V3h5v18H3Zm4-4h1m4 0h1m4 0h1"/>',
			],
			[
				/bank|company|tax|account.*setup/,
				'<path d="m3 8 9-5 9 5H3Zm0 13h18M5 11v7m5-7v7m4-7v7m5-7v7"/>',
			],
			[
				/payment|cash|capital|budget|profit|revenue|expense|invoice|billing|receivable|payable/,
				'<rect x="3" y="5" width="18" height="15" rx="3"/><path d="M3 10h18m-6 5h3M7 3v2"/>',
			],
			[/quality|approval|verified/, '<path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Zm-4 9 3 3 5-6"/>'],
			[
				/report|overview|home|analytics|intelligence|ledger|trial|balance|register/,
				'<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M7 16v-4m5 4V7m5 9v-6"/>',
			],
			[
				/setting|integration|engineering|bom|routing/,
				'<path d="m14 4 1-2 3 2-1 2 2 3 3 1v4l-3 1-2 3 1 2-3 2-1-2h-4l-1 2-3-2 1-2-2-3-3-1v-4l3-1 2-3-1-2 3-2 1 2h4Z"/><circle cx="12" cy="12" r="3"/>',
			],
			[
				/delivery|transport/,
				'<path d="M3 5h11v12H3V5Zm11 5h4l3 4v3h-7"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
			],
			[/project|cost center/, '<path d="M3 7V5h7l2 3h9v12H3V7Z"/><path d="M7 13h10m-10 3h6"/>'],
		];
		const shape =
			shapes.find(([pattern]) => pattern.test(text))?.[1] ||
			'<path d="M6 3h9l4 4v14H6V3Zm9 0v5h4M9 12h7m-7 4h7"/>';
		return `<svg class="sarathi-ui-icon" width="16" height="16" style="width:16px;height:16px;flex-shrink:0;vertical-align:middle;display:inline-block;" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">${shape}</svg>`;
	}

	constructor(wrapper) {
		this.wrapper = $(wrapper);
		// Purge any existing DOM nodes from wrapper before building page
		this.wrapper.empty();

		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: "Sarathi Owner Dashboard",
			single_column: true,
			hide_sidebar: true,
		});

		this.page.main.empty();

		frappe.provide("frappe.templates");
		frappe.templates["sarathiownertower"] = `<div class="sod-wrapper">
  <!-- Top View Switcher Bar -->
  <div class="sod-switcher-bar">
    <span class="sod-switcher-label">Dashboard View:</span>
    <button class="sod-switcher-btn active" data-action="switch-owner">
      <span class="sod-switcher-icon">👑</span> Owner Executive View
    </button>
    <button class="sod-switcher-btn" data-action="switch-pm">
      <span class="sod-switcher-icon">🏭</span> Production Manager View
    </button>
  </div>

  <div class="sod-app">
    <!-- Left Navigation Sidebar -->
    <aside class="sod-side">
      <nav id="sod-nav" class="sod-nav" aria-label="Owner navigation"></nav>
    </aside>

    <!-- Main Content Area -->
    <main class="sod-main">
      <div class="sod-top">
        <span class="sod-breadcrumb" id="sod-breadcrumb">Workspace /
          <a href="javascript:void(0)" class="sod-link" data-action="go-home">Owner</a>
          / <b id="sod-crumb-text">Home</b></span>
        <div style="display: flex; align-items: center; gap: 12px">
          <button class="sod-btn-glass sod-btn-refresh-top" data-action="refresh" title="Sync all live values">
            ↻ Refresh
          </button>
          <div class="sod-live-status-pill" id="sod-live-status-pill"
            title="Last successful ERPNext record refresh">
            <span class="sod-pulse-dot"></span>
            <span id="sod-live-status-text">Waiting for records</span>
          </div>
          <div class="sod-user-pill">
            <span id="sod-live-time"></span> &nbsp;
            <span class="sod-avatar" id="sod-avatar-initials">OW</span>
          </div>
        </div>
      </div>

      <!-- Global Filter Bar: Customer | Project | Status | Date Range | Submit -->
      <section class="sod-filters" id="sod-filters" aria-label="Global Filters">
        <!-- 1. Customer Search & Suggestion Combo with Cancel Mark -->
        <div class="sod-filter-group sod-combo-group">
          <label for="sod-filter-customer-input">Customer</label>
          <div class="sod-search-combo">
            <input type="text" id="sod-filter-customer-input" class="sod-combo-input" placeholder="All Customers"
              autocomplete="off" />
            <button type="button" class="sod-combo-clear" id="sod-clear-customer-btn" aria-label="Clear customer" title="Clear customer" tabindex="-1">
              <svg viewBox="0 0 20 20" width="14" height="14" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </button>
            <button type="button" class="sod-combo-chevron" id="sod-combo-customer-btn"
              aria-label="Toggle customer options">▾</button>
            <div class="sod-suggestions-menu" id="sod-customer-suggestions"></div>
          </div>
          <select id="sod-filter-customer" class="sod-hidden-select" style="display:none;" aria-label="Customer filter">
            <option value="">All Customers</option>
          </select>
        </div>

        <!-- 2. Project Search & Suggestion Combo with Cancel Mark -->
        <div class="sod-filter-group sod-combo-group">
          <label for="sod-filter-project-input">Project</label>
          <div class="sod-search-combo">
            <input type="text" id="sod-filter-project-input" class="sod-combo-input" placeholder="All Projects"
              autocomplete="off" />
            <button type="button" class="sod-combo-clear" id="sod-clear-project-btn" aria-label="Clear project" title="Clear project" tabindex="-1">
              <svg viewBox="0 0 20 20" width="14" height="14" fill="currentColor">
                <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
              </svg>
            </button>
            <button type="button" class="sod-combo-chevron" id="sod-combo-project-btn"
              aria-label="Toggle project options">▾</button>
            <div class="sod-suggestions-menu" id="sod-project-suggestions"></div>
          </div>
          <select id="sod-filter-project" class="sod-hidden-select" style="display:none;" aria-label="Project filter">
            <option value="">All Projects</option>
          </select>
        </div>

        <!-- 3. Status Filter -->
        <div class="sod-filter-group">
          <label for="sod-filter-status">Status</label>
          <select id="sod-filter-status" class="sod-select" aria-label="Project status filter">
            <option value="">All Statuses</option>
            <option value="Open">Open</option>
            <option value="On Hold">On Hold</option>
            <option value="Completed">Completed</option>
            <option value="Cancelled">Cancelled</option>
          </select>
        </div>

        <!-- 4. Date Range Filter with Floating Custom Range Picker (Zero Overlap) -->
        <div class="sod-filter-group sod-combo-group sod-date-group">
          <label for="sod-filter-date">Date Range</label>
          <div class="sod-date-wrapper">
            <select id="sod-filter-date" class="sod-select" aria-label="Date Range filter">
              <option value="all">All Dates</option>
              <option value="today">Today</option>
              <option value="this_week">This Week</option>
              <option value="this_month">This Month</option>
              <option value="last_month">Last Month</option>
              <option value="this_quarter">This Quarter</option>
              <option value="this_year">This Fiscal Year</option>
              <option value="custom">Custom Date Range 📅</option>
            </select>

            <!-- Floating Custom Date Range Popover (Generous Full Width, Zero Overlap) -->
            <div class="sod-date-popover" id="sod-date-popover">
              <div class="sod-date-popover-header">
                <span>📅 Custom Date Range</span>
                <button type="button" class="sod-date-popover-close" id="sod-date-popover-close"
                  aria-label="Close date picker">✕</button>
              </div>
              <div class="sod-date-popover-fields">
                <div class="sod-date-field-col">
                  <label for="sod-filter-from-date">From Date</label>
                  <input type="date" id="sod-filter-from-date" class="sod-date-full-input" aria-label="From Date" />
                </div>
                <div class="sod-date-popover-arrow">→</div>
                <div class="sod-date-field-col">
                  <label for="sod-filter-to-date">To Date</label>
                  <input type="date" id="sod-filter-to-date" class="sod-date-full-input" aria-label="To Date" />
                </div>
              </div>
              <div class="sod-date-popover-footer">
                <button type="button" class="sod-btn-date-clear" id="sod-date-clear-btn">Clear</button>
                <button type="button" class="sod-btn-date-apply" id="sod-date-apply-btn">Apply Range</button>
              </div>
            </div>
          </div>
        </div>

        <!-- 5. Submit Button -->
        <div class="sod-filter-group sod-submit-group">
          <button type="button" class="sod-btn-submit" id="sod-filter-submit-btn">
            <span>Submit</span>
          </button>
        </div>
      </section>

      <!-- Active Content Container -->
      <div id="sod-content" class="sod-content">
        <div class="sod-loading">
          <div class="sod-spinner"></div>
          <p>Connecting to ERPNext and aggregating metrics…</p>
        </div>
      </div>
    </main>
  </div>

  <!-- Stage Inspection Modal Overlay -->
  <div id="sod-stage-overlay" class="sod-detail-overlay">
    <div class="sod-detail-card" role="dialog" aria-modal="true">
      <div class="sod-modal-head">
        <h2 id="sod-modal-title">Stage Details</h2>
        <button class="sod-btn-close" id="sod-modal-close" aria-label="Close dialog">
          ✕
        </button>
      </div>
      <div id="sod-modal-body" class="sod-modal-body"></div>
      <div class="sod-modal-foot" id="sod-modal-foot"></div>
    </div>
  </div>
</div>`;

		this.root = $(frappe.render_template("sarathiownertower", {})).appendTo(this.page.main)[0];
		this.sharedUI = frappe.sarathiUI.enhance(this.root);

		// Purge any duplicate sod-wrapper, footers, or switcher bars
		$(wrapper).find(".sod-wrapper").not(this.root).remove();
		$(wrapper).find(".sod-footer").remove();
		$(".sod-wrapper ~ .sod-wrapper").remove();

		this.pagesConfig = [
			[
				"Owner Home",
				"◈",
				"Executive command center: financial health, order book, live charts, and manufacturing governance.",
				"home",
				"OPERATIONS",
			],
			[
				"Projects",
				"▦",
				"Project portfolio, profitability margins, budget variance, and delivery status.",
				"projects",
				"OPERATIONS",
			],
			[
				"Project Detail",
				"▤",
				"Detailed project financials, budget vs actuals, and executive pipeline.",
				"project_detail",
				"OPERATIONS",
			],
			[
				"Customers",
				"♧",
				"Customer concentration, order commitments, and accounts receivable exposure.",
				"customers",
				"OPERATIONS",
			],
			[
				"Sales Orders",
				"▣",
				"Commercial order book, fulfillment backlog, and delivery schedule adherence.",
				"sales_orders",
				"OPERATIONS",
			],
			[
				"Manufacturing",
				"⚙",
				"Production throughput, output velocity, and factory schedule risk.",
				"manufacturing",
				"OPERATIONS",
			],
			[
				"Working Capital & Stock",
				"◫",
				"Inventory asset valuation, warehouse capital distribution, and shortage risks.",
				"stock_quality",
				"OPERATIONS",
			],
			// Accounting Modules (The 9 sections in ERPNext Desk / Accounting)
			[
				"Invoicing",
				"📑",
				"Customer & supplier invoicing, billing ledger, credit/debit notes, and receivables.",
				"invoicing",
				"ACCOUNTING & FINANCE",
			],
			[
				"Payments",
				"💳",
				"Realized receipts, vendor payments, journal entries, and ledger reconciliation.",
				"payments",
				"ACCOUNTING & FINANCE",
			],
			[
				"Financial Reports",
				"📊",
				"Official Balance Sheet, Profit and Loss Statement, Cash Flow, and General Ledger.",
				"financial_reports",
				"ACCOUNTING & FINANCE",
			],
			[
				"Accounts Setup",
				"⚙️",
				"Chart of accounts, cost centers, accounting dimensions, currencies, and fiscal periods.",
				"accounts_setup",
				"ACCOUNTING & FINANCE",
			],
			[
				"Taxes",
				"🏛️",
				"Tax rules, sales & purchase tax templates, TDS withholding, and tax computation.",
				"taxes",
				"ACCOUNTING & FINANCE",
			],
			[
				"Banking",
				"🏦",
				"Bank accounts, liquid cash reserves, bank reconciliation statement, and clearance.",
				"banking",
				"ACCOUNTING & FINANCE",
			],
			[
				"Budget",
				"📉",
				"Cost center budgets, variance tracking, quarterly allocations, and expense controls.",
				"budget",
				"ACCOUNTING & FINANCE",
			],
			[
				"Share Management",
				"🤝",
				"Company shareholders, share ledger, equity transfers, and balance register.",
				"share_management",
				"ACCOUNTING & FINANCE",
			],
			[
				"Subscription",
				"🔁",
				"Customer & vendor recurring subscriptions, subscription plans, and billing intervals.",
				"subscription",
				"ACCOUNTING & FINANCE",
			],
			// Intelligence & Reports
			[
				"Executive Decision Reports",
				"▥",
				"Run live ERPNext query reports in-memory inside the tower.",
				"reports",
				"INTELLIGENCE",
			],
		];

		this.currentPage = 0;
		this.context = null;
		this.activeData = null;
		this.chartInstances = {};
		this.refreshTimer = null;
		this.selectedProject = "";
		this.currentReportName = "Accounts Receivable";
		this.activeReportData = null;
		this.reportSearchQuery = "";
		this.companyOptions = [];
		this.customerOptions = [];
		this.projectOptions = [];

		window.scrollTo(0, 0);

		this.initElements();
		this.bindEvents();
		this.setupSearchableCombos();
		this.setupDateRangeFilters();
		this.initRealtimeListener();
		this.renderNav();
		this.loadContext();
	}

	initElements() {
		this.$el = $(this.root);
		this.$el.find(".scm-owner-nav, .scm-launcher").remove();
		this.$nav = this.$el.find("#sod-nav");
		this.$nav.find(".scm-owner-nav").remove();
		this.$content = this.$el.find("#sod-content");
		this.$title = this.$el.find("#sod-title");
		this.$subtitle = this.$el.find("#sod-subtitle");
		this.$breadcrumb = this.$el.find("#sod-crumb-text");
		this.$modal = this.$el.find("#sod-stage-overlay");
		this.$modalTitle = this.$el.find("#sod-modal-title");
		this.$modalBody = this.$el.find("#sod-modal-body");
		this.$modalFoot = this.$el.find("#sod-modal-foot");

		// Live Date/Time
		const now = new Date();
		const options = { day: "numeric", month: "short", year: "numeric" };
		this.$el.find("#sod-live-time").text(now.toLocaleDateString("en-IN", options));

		// User Avatar Initials
		const fullName = frappe.session.user_fullname || frappe.session.user || "Owner";
		const initials = fullName
			.split(" ")
			.map((n) => n[0])
			.join("")
			.substring(0, 2)
			.toUpperCase();
		this.$el.find("#sod-avatar-initials").text(initials || "OW");

		// Injected Dynamic Module Sections Styles (Guarantees zero-cache rendering)
		if (!document.getElementById("sod-sections-dynamic-style")) {
			const styleEl = document.createElement("style");
			styleEl.id = "sod-sections-dynamic-style";
			styleEl.textContent = `
        .sod-sections-container {
          margin: 20px 0 !important;
          background: #f8fafc !important;
          border: 1px solid #e2e8f0 !important;
          border-radius: 16px !important;
          padding: 22px 24px !important;
          box-shadow: 0 2px 10px rgba(15, 23, 42, 0.03) !important;
        }
        .sod-sections-header {
          display: flex !important;
          justify-content: space-between !important;
          align-items: flex-end !important;
          margin-bottom: 20px !important;
          padding-bottom: 14px !important;
          border-bottom: 1px solid #e2e8f0 !important;
          gap: 14px !important;
          flex-wrap: wrap !important;
        }
        .sod-sections-kicker {
          font-size: 11px !important;
          font-weight: 800 !important;
          letter-spacing: 1.2px !important;
          text-transform: uppercase !important;
          color: #4f46e5 !important;
          display: block !important;
          margin-bottom: 4px !important;
        }
        .sod-sections-title {
          font-size: 19px !important;
          font-weight: 700 !important;
          color: #0f172a !important;
          margin: 0 !important;
        }
        .sod-sections-count-pill {
          background: #ffffff !important;
          border: 1px solid #cbd5e1 !important;
          border-radius: 20px !important;
          padding: 5px 14px !important;
          font-size: 12px !important;
          font-weight: 600 !important;
          color: #475569 !important;
          box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        }
        .sod-sections-grid {
          display: grid !important;
          grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)) !important;
          gap: 18px !important;
        }
        .sod-section-box {
          background: #ffffff !important;
          border: 1px solid #e2e8f0 !important;
          border-radius: 12px !important;
          padding: 16px 18px !important;
          box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04) !important;
          display: flex !important;
          flex-direction: column !important;
        }
        .sod-section-box:hover {
          box-shadow: 0 5px 15px rgba(15, 23, 42, 0.07) !important;
        }
        .sod-section-box-header {
          display: flex !important;
          justify-content: space-between !important;
          align-items: center !important;
          margin-bottom: 14px !important;
          padding-bottom: 10px !important;
          border-bottom: 1px solid #f1f5f9 !important;
        }
        .sod-section-box-title-wrap {
          display: flex !important;
          align-items: center !important;
          gap: 10px !important;
        }
        .sod-section-box-icon {
          width: 28px !important;
          height: 28px !important;
          border-radius: 7px !important;
          background: #eef2ff !important;
          color: #4f46e5 !important;
          display: inline-flex !important;
          align-items: center !important;
          justify-content: center !important;
          flex-shrink: 0 !important;
        }
        .sod-section-box-icon svg {
          width: 16px !important;
          height: 16px !important;
        }
        .sod-section-box-title {
          font-size: 15px !important;
          font-weight: 700 !important;
          color: #0f172a !important;
          margin: 0 !important;
        }
        .sod-section-box-badge {
          background: #f1f5f9 !important;
          color: #475569 !important;
          font-size: 11px !important;
          font-weight: 700 !important;
          padding: 3px 9px !important;
          border-radius: 12px !important;
          border: 1px solid #e2e8f0 !important;
        }
        .sod-section-items-grid {
          display: flex !important;
          flex-direction: column !important;
          gap: 8px !important;
        }
        .sod-module-item-card {
          display: flex !important;
          justify-content: space-between !important;
          align-items: center !important;
          background: #f8fafc !important;
          border: 1px solid #e2e8f0 !important;
          border-radius: 8px !important;
          padding: 8px 12px !important;
          gap: 10px !important;
          transition: all 0.15s ease !important;
        }
        .sod-module-item-card:hover {
          background: #ffffff !important;
          border-color: #cbd5e1 !important;
          box-shadow: 0 3px 8px rgba(15, 23, 42, 0.05) !important;
          transform: translateY(-1px) !important;
        }
        .sod-module-item-main {
          display: flex !important;
          align-items: center !important;
          gap: 10px !important;
          cursor: pointer !important;
          flex: 1 !important;
          min-width: 0 !important;
        }
        .sod-module-item-icon {
          width: 24px !important;
          height: 24px !important;
          border-radius: 6px !important;
          background: #ffffff !important;
          border: 1px solid #e2e8f0 !important;
          color: #64748b !important;
          display: inline-flex !important;
          align-items: center !important;
          justify-content: center !important;
          flex-shrink: 0 !important;
        }
        .sod-module-item-icon svg {
          width: 14px !important;
          height: 14px !important;
        }
        .sod-module-item-text {
          display: flex !important;
          align-items: center !important;
          gap: 8px !important;
          min-width: 0 !important;
          flex-wrap: wrap !important;
        }
        .sod-module-item-name {
          font-size: 13px !important;
          font-weight: 600 !important;
          color: #1e293b !important;
          white-space: nowrap !important;
          overflow: hidden !important;
          text-overflow: ellipsis !important;
        }
        .sod-module-item-card:hover .sod-module-item-name {
          color: #4f46e5 !important;
        }
        .sod-module-item-kind-tag {
          font-size: 9.5px !important;
          font-weight: 700 !important;
          text-transform: uppercase !important;
          letter-spacing: 0.5px !important;
          padding: 2px 6px !important;
          border-radius: 4px !important;
          display: inline-block !important;
          line-height: 1.2 !important;
        }
        .sod-module-item-kind-tag.doctype {
          background: #dbeafe !important;
          color: #1e40af !important;
          border: 1px solid #bfdbfe !important;
        }
        .sod-module-item-kind-tag.report {
          background: #fef3c7 !important;
          color: #92400e !important;
          border: 1px solid #fde68a !important;
        }
        .sod-module-item-kind-tag.workspace {
          background: #ede9fe !important;
          color: #5b21b6 !important;
          border: 1px solid #ddd6fe !important;
        }
        .sod-module-item-kind-tag.dashboard {
          background: #d1fae5 !important;
          color: #065f46 !important;
          border: 1px solid #a7f3d0 !important;
        }
        .sod-module-item-actions {
          display: flex !important;
          align-items: center !important;
          gap: 6px !important;
          flex-shrink: 0 !important;
        }
        .sod-item-btn-new {
          font-size: 11px !important;
          font-weight: 600 !important;
          color: #4f46e5 !important;
          background: #eef2ff !important;
          border: 1px solid #c7d2fe !important;
          border-radius: 5px !important;
          padding: 2px 7px !important;
          text-decoration: none !important;
          transition: all 0.15s ease !important;
          display: inline-flex !important;
          align-items: center !important;
        }
        .sod-item-btn-new:hover {
          background: #4f46e5 !important;
          color: #ffffff !important;
        }
        .sod-item-btn-desk {
          font-size: 11px !important;
          font-weight: 700 !important;
          color: #64748b !important;
          background: #ffffff !important;
          border: 1px solid #cbd5e1 !important;
          border-radius: 5px !important;
          padding: 2px 7px !important;
          text-decoration: none !important;
          transition: all 0.15s ease !important;
          display: inline-flex !important;
          align-items: center !important;
        }
        .sod-item-btn-desk:hover {
          background: #0f172a !important;
          color: #ffffff !important;
          border-color: #0f172a !important;
        }
      `;
			document.head.appendChild(styleEl);
		}
	}

	/* -------------------------------------------------------------
     REAL-TIME SOCKET.IO & LIVE CHANGING VALUES
  ------------------------------------------------------------- */
	initRealtimeListener() {
		const self = this;
		if (window.frappe && frappe.realtime) {
			// Listen for custom broadcast from sarathi_owner backend
			frappe.realtime.on("sarathi_owner_live_change", (data) => {
				self.handleLiveSocketChange(data);
			});

			// Listen for visibility control tower changes
			frappe.realtime.on("sarathi_dashboard_changed", (data) => {
				self.handleLiveSocketChange(data);
			});

			// Listen for standard Frappe document events across all operational doctypes
			frappe.realtime.on("doc_update", (data) => {
				if (
					data &&
					data.doctype &&
					[
						"Project",
						"Company",
						"Customer",
						"Sales Order",
						"Sales Invoice",
						"Payment Entry",
						"Work Order",
						"Stock Entry",
						"Delivery Note",
						"BOM",
						"Task",
						"Warehouse",
						"Item",
						"Job Card",
						"Quality Inspection",
						"Production Plan",
						"Purchase Order",
						"Purchase Receipt",
						"Quotation",
						"Opportunity",
						"Lead",
					].includes(data.doctype)
				) {
					self.handleLiveSocketChange(data);
				}
			});
		}
	}

	handleLiveSocketChange(data = {}) {
		if (!this.visible) return;
		const dt = data.doctype || "Transaction";
		const name = data.name || "";
		this.showLiveToast(`⚡ Live Update: ${dt} ${name} updated`);

		// Dynamically refresh the dropdown options if a Company, Customer, or Project was modified
		if (!data.doctype || ["Company", "Customer", "Project"].includes(dt)) {
			this.refreshFilterDropdownsOnly();
		}

		// Smoothly re-fetch without wiping the page with full-screen loading spinner
		this.smoothRefresh();
	}

	refreshFilterDropdownsOnly() {
		const selectedCompany = this.$el.find("#sod-filter-company").val() || "";
		frappe.call({
			method: "sarathi_owner.api.owner_dashboard.get_owner_context",
			args: { company: selectedCompany },
			callback: (r) => {
				if (r.message) {
					this.context = r.message;
					this.populateFilterDropdowns();
				}
			},
		});
	}

	showLiveToast(msg) {
		$(".sod-toast").remove();
		const $toast = $(`
      <div class="sod-toast">
        <span class="sod-pulse-dot"></span>
        <span>${frappe.utils.escape_html(msg)}</span>
      </div>
    `).appendTo(document.body);

		setTimeout(() => {
			$toast.fadeOut(400, () => $toast.remove());
		}, 3800);
	}

	bindEvents() {
		const self = this;

		// View Switcher
		this.$el.on("click", "[data-action='switch-pm']", function () {
			frappe.set_route("sarathicontroltower");
		});
		this.$el.on("click", "[data-action='switch-owner']", function () {
			self.selectPage(0);
		});

		// Refresh action
		// Refresh action (Clears server and client cache, reloads context, refreshes page)
		this.$el.on("click", "[data-action='refresh']", function () {
			const $btn = $(this);
			$btn.addClass("sod-spinning");
			if (typeof localStorage !== "undefined") {
				try {
					localStorage.removeItem("_page:sarathiownertower");
					localStorage.removeItem("page:sarathiownertower");
					localStorage.removeItem("route:sarathiownertower");
				} catch (e) {
					// Ignore storage exceptions in restricted environments
				}
			}
			self.activeData = null;
			frappe.call({
				method: "sarathi_owner.api.owner_dashboard.clear_owner_cache",
				callback: () => {
					self.loadContext();
					self.refreshCurrentPage();
					setTimeout(() => $btn.removeClass("sod-spinning"), 600);
				},
				error: () => {
					self.loadContext();
					self.refreshCurrentPage();
					setTimeout(() => $btn.removeClass("sod-spinning"), 600);
				},
			});
		});

		// Breadcrumb navigation
		this.$el.on("click", "[data-action='go-home']", function () {
			self.selectPage(0);
		});

		// Modal Close
		this.$el.find("#sod-modal-close").on("click", function () {
			self.$modal.removeClass("show");
		});
		this.$modal.on("click", function (e) {
			if (e.target === this) {
				self.$modal.removeClass("show");
			}
		});
		this.$modal.on("click", "[data-project-drill]", function () {
			const projectName = $(this).data("project-drill");
			if (projectName) {
				self.$modal.removeClass("show");
				self.selectedProject = projectName;
				self.$el.find("#sod-filter-project").val(projectName);
				self.goToPageByKey("project_detail");
			}
		});

		// Global Reactive Filters
		this.$el.find("#sod-filter-date, #sod-filter-status").on("change", function () {
			self.refreshCurrentPage();
		});

		// Submit Button
		this.$el.find("#sod-filter-submit-btn").on("click", function () {
			const $btn = $(this);
			$btn.css("opacity", "0.75");
			self.refreshCurrentPage();
			setTimeout(() => $btn.css("opacity", "1"), 250);
		});

		this.$content.on("click", "[data-quick-detail]", (event) => {
			const action = this.activeData?.shortcuts?.[Number(event.currentTarget.dataset.quickDetail)];
			if (action) this.showQuickDetails(action);
		});

		this.$content.on("click", "[data-section-quick]", (event) => {
			const parts = String(event.currentTarget.dataset.sectionQuick || "").split("_");
			const sIdx = Number(parts[0]);
			const iIdx = Number(parts[1]);
			const sec = this.activeData?.sections?.[sIdx];
			const item = sec?.items?.[iIdx];
			if (item) this.showQuickDetails(item);
		});

		// Interactive Card Click Handlers - Shows Focused Form-Type Details Modal
		this.$content.on("click", ".sod-card", function (e) {
			if ($(e.target).closest("a, button").length) return;
			const $card = $(this);
			const label =
				$card.find(".sod-label").text().trim() ||
				$card.find("strong").text().trim() ||
				"Metric Details";
			const value =
				$card.find(".sod-kpi-val, strong").text().trim() || $card.find("strong").text().trim() || "—";
			const desc = $card.find("small").text().trim() || "";
			const action = $card.data("action") || "";
			const route = $card.data("route") || "";
			self.showCardDetailModal(label, value, desc, action, route);
		});

		// Project Drill-Down
		this.$content.on("click", "[data-project-drill]", function (e) {
			if ($(e.target).closest("a").length) return;
			const projectName = $(this).data("project-drill");
			if (projectName) {
				self.selectedProject = projectName;
				self.$el.find("#sod-filter-project").val(projectName);
				self.goToPageByKey("project_detail");
			}
		});

		// In-Page Project Switcher Change
		this.$content.on("change", "#sod-inpage-project-select", function () {
			const pName = $(this).val();
			if (pName) {
				self.selectedProject = pName;
				self.$el.find("#sod-filter-project").val(pName);
				self.refreshCurrentPage();
			}
		});

		// Accounts Section Click Actions
		this.$content.on("click", "[data-action='go-to-invoicing']", function () {
			self.goToPageByKey("invoicing");
		});
		this.$content.on("click", "[data-action='open-advance-orders']", function () {
			window.open("/app/sales-order?status=To%20Deliver%20and%20Bill", "_blank");
		});
		this.$content.on("click", "[data-action='open-sales-invoices']", function () {
			window.open("/app/sales-invoice", "_blank");
		});
	}

	setupSearchableCombos() {
		const self = this;
		const combos = [
			{ key: "customer", placeholder: "All Customers" },
			{ key: "project", placeholder: "All Projects" },
		];

		combos.forEach(({ key, placeholder }) => {
			const $input = self.$el.find(`#sod-filter-${key}-input`);
			const $hidden = self.$el.find(`#sod-filter-${key}`);
			const $btn = self.$el.find(`#sod-combo-${key}-btn`);
			const $clear = self.$el.find(`#sod-clear-${key}-btn`);
			const $dropdown = self.$el.find(`#sod-${key}-suggestions`);

			const updateClearVisibility = () => {
				const val = ($input.val() || "").trim();
				const hiddenVal = ($hidden.val() || "").trim();
				if (val || hiddenVal) {
					$clear.addClass("visible");
				} else {
					$clear.removeClass("visible");
				}
			};

			const renderMenu = (query = "") => {
				const options = (self[`${key}Options`] || []).slice();
				const filtered = query
					? options.filter(
							(o) =>
								(o.label || "").toLowerCase().includes(query.toLowerCase()) ||
								(o.value || "").toLowerCase().includes(query.toLowerCase())
					  )
					: options;

				if (!filtered.length) {
					$dropdown.html(
						'<div style="padding:8px 12px; font-size:12px; color:#94a3b8;">No matching options</div>'
					);
				} else {
					let html = "";
					filtered.forEach((opt) => {
						const isSelected = $hidden.val() === opt.value;
						let displayLabel = frappe.utils.escape_html(opt.label || opt.value || "");
						if (query && opt.value) {
							const regex = new RegExp(
								`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`,
								"gi"
							);
							displayLabel = displayLabel.replace(regex, "<mark>$1</mark>");
						}
						html += `
              <div class="sod-suggestion-item ${
					isSelected ? "active" : ""
				}" data-val="${frappe.utils.escape_html(opt.value)}">
                <span>${displayLabel}</span>
                ${isSelected ? '<span style="font-size:11px;">✓</span>' : ""}
              </div>
            `;
					});
					$dropdown.html(html);
				}
				$dropdown.addClass("show");
			};

			// Input typing / focus
			$input.on("focus", function () {
				renderMenu($(this).val().trim());
				updateClearVisibility();
			});

			$input.on("input", function () {
				const query = $(this).val().trim();
				renderMenu(query);
				updateClearVisibility();
			});

			$input.on("keydown", function (e) {
				if (e.key === "Enter") {
					e.preventDefault();
					$dropdown.removeClass("show");
					self.refreshCurrentPage();
				}
			});

			// Cancel / Clear mark click
			$clear.on("click", function (e) {
				e.stopPropagation();
				$input.val("");
				$hidden.val("");
				if (key === "project") {
					self.selectedProject = "";
				}
				updateClearVisibility();
				$dropdown.removeClass("show");
				self.refreshCurrentPage();
			});

			// Chevron toggle
			$btn.on("click", function (e) {
				e.stopPropagation();
				if ($dropdown.hasClass("show")) {
					$dropdown.removeClass("show");
				} else {
					$(".sod-suggestions-menu").removeClass("show");
					renderMenu("");
					$input.focus();
				}
			});

			// Item selection
			$dropdown.on("click", ".sod-suggestion-item", function (e) {
				e.stopPropagation();
				const val = $(this).data("val") || "";
				const label = $(this).text().replace("✓", "").trim();
				$hidden.val(val);
				$input.val(val ? label : "");
				if (key === "project") {
					self.selectedProject = val;
				}
				updateClearVisibility();
				$dropdown.removeClass("show");
			});
		});

		// Close when clicking outside
		$(document).on("click", (e) => {
			if (!$(e.target).closest(".sod-search-combo").length) {
				$(".sod-suggestions-menu").removeClass("show");
			}
		});
	}

	setupDateRangeFilters() {
		const self = this;
		const $preset = this.$el.find("#sod-filter-date");
		const $popover = this.$el.find("#sod-date-popover");
		const $from = this.$el.find("#sod-filter-from-date");
		const $to = this.$el.find("#sod-filter-to-date");

		const formatDateIso = (d) => {
			const year = d.getFullYear();
			const month = String(d.getMonth() + 1).padStart(2, "0");
			const day = String(d.getDate()).padStart(2, "0");
			return `${year}-${month}-${day}`;
		};

		$preset.on("change", function () {
			const val = $(this).val();
			const now = new Date();

			if (val === "custom") {
				$popover.addClass("show");
				return;
			}

			$popover.removeClass("show");

			if (val === "today") {
				const todayStr = formatDateIso(now);
				$from.val(todayStr);
				$to.val(todayStr);
			} else if (val === "this_week") {
				const day = now.getDay();
				const diff = now.getDate() - day + (day === 0 ? -6 : 1);
				const mon = new Date(now.setDate(diff));
				const sun = new Date(mon);
				sun.setDate(mon.getDate() + 6);
				$from.val(formatDateIso(mon));
				$to.val(formatDateIso(sun));
			} else if (val === "this_month") {
				const first = new Date(now.getFullYear(), now.getMonth(), 1);
				const last = new Date(now.getFullYear(), now.getMonth() + 1, 0);
				$from.val(formatDateIso(first));
				$to.val(formatDateIso(last));
			} else if (val === "last_month") {
				const first = new Date(now.getFullYear(), now.getMonth() - 1, 1);
				const last = new Date(now.getFullYear(), now.getMonth(), 0);
				$from.val(formatDateIso(first));
				$to.val(formatDateIso(last));
			} else if (val === "this_quarter") {
				const qMonth = Math.floor(now.getMonth() / 3) * 3;
				const first = new Date(now.getFullYear(), qMonth, 1);
				const last = new Date(now.getFullYear(), qMonth + 3, 0);
				$from.val(formatDateIso(first));
				$to.val(formatDateIso(last));
			} else if (val === "this_year") {
				const yr = now.getMonth() >= 3 ? now.getFullYear() : now.getFullYear() - 1;
				const first = new Date(yr, 3, 1);
				const last = new Date(yr + 1, 2, 31);
				$from.val(formatDateIso(first));
				$to.val(formatDateIso(last));
			} else if (val === "all") {
				$from.val("");
				$to.val("");
			}
			self.refreshCurrentPage();
		});

		// Close button inside popover
		this.$el.find("#sod-date-popover-close").on("click", function (e) {
			e.stopPropagation();
			$popover.removeClass("show");
		});

		// Apply button inside popover
		this.$el.find("#sod-date-apply-btn").on("click", function (e) {
			e.stopPropagation();
			$popover.removeClass("show");
			$preset.val("custom");
			self.refreshCurrentPage();
		});

		// Clear button inside popover
		this.$el.find("#sod-date-clear-btn").on("click", function (e) {
			e.stopPropagation();
			$from.val("");
			$to.val("");
			$preset.val("all");
			$popover.removeClass("show");
			self.refreshCurrentPage();
		});

		// Close when clicking outside date filter
		$(document).on("click", (e) => {
			if (!$(e.target).closest(".sod-date-group").length) {
				$popover.removeClass("show");
			}
		});
	}

	goToPageByKey(key) {
		const idx = this.pagesConfig.findIndex((p) => p[3] === key);
		if (idx !== -1) {
			this.selectPage(idx);
		}
	}

	renderNav() {
		this.$nav.empty();
		let currentCategory = "";
		let $accountingMenu = null;

		this.pagesConfig.forEach(([title, icon, , pageKey, category], idx) => {
			// 1. Group / Section boundary handling
			if (category && category !== currentCategory) {
				currentCategory = category;

				if (category === "ACCOUNTING & FINANCE") {
					const isCollapsed = !this.accountingDropdownOpen;
					const $group = $(`
            <div class="sod-nav-dropdown-group ${isCollapsed ? "collapsed" : ""}" id="sod-accounting-group">
              <button class="sod-nav-dropdown-toggle" id="sod-accounting-toggle" type="button" aria-expanded="${!isCollapsed}" title="Click to toggle Accounting & Finance modules">
                <div class="sod-nav-dropdown-left">
                  <span class="sod-icon">🏛️</span>
                  <span class="sod-nav-dropdown-title">Accounting & Finance</span>
                </div>
                <div class="sod-nav-dropdown-right">
                  <span class="sod-nav-dropdown-badge">9</span>
                  <span class="sod-nav-dropdown-arrow">▼</span>
                </div>
              </button>
              <div class="sod-nav-dropdown-menu" id="sod-accounting-menu"></div>
            </div>
          `);

					$group.find("#sod-accounting-toggle").on("click", (e) => {
						e.preventDefault();
						this.accountingDropdownOpen = !this.accountingDropdownOpen;
						$group.toggleClass("collapsed", !this.accountingDropdownOpen);
						$group
							.find("#sod-accounting-toggle")
							.attr("aria-expanded", this.accountingDropdownOpen);
					});

					this.$nav.append($group);
					$accountingMenu = $group.find("#sod-accounting-menu");
				} else {
					$accountingMenu = null;
					const catIcons = {
						OPERATIONS: "⚙️",
						INTELLIGENCE: "💡",
					};
					const catIcon = catIcons[category] || "✦";
					this.$nav.append(`
            <div class="sod-nav-section-title">
              <span class="sod-nav-section-icon">${catIcon}</span>
              <span>${frappe.utils.escape_html(category)}</span>
            </div>
          `);
				}
			}

			// 2. Render item button
			const $btn = $(`
        <button class="${
			idx === this.currentPage ? "active" : ""
		}" data-page="${idx}" data-key="${frappe.utils.escape_html(
				pageKey || ""
			)}" title="${frappe.utils.escape_html(title)}">
          <span class="sod-icon">${this.workspaceIcon(title)}</span>
          <span class="sod-nav-label">${frappe.utils.escape_html(title)}</span>
        </button>
      `);
			$btn.on("click", () => this.selectPage(idx));

			if (category === "ACCOUNTING & FINANCE" && $accountingMenu) {
				$accountingMenu.append($btn);
			} else {
				this.$nav.append($btn);
			}
		});
		this.$nav.find(".scm-owner-nav").remove();
	}

	loadContext() {
		frappe.call({
			method: "sarathi_owner.api.owner_dashboard.get_owner_context",
			callback: (r) => {
				if (r.message) {
					this.context = r.message;
					this.populateFilterDropdowns();
					this.selectPage(0);
				}
			},
		});
	}

	populateFilterDropdowns() {
		if (!this.context) return;

		// 1. Customers
		this.customerOptions = [{ value: "", label: "All Customers" }];
		const $cust = this.$el.find("#sod-filter-customer");
		const currentCust = $cust.val();
		$cust.find("option:not(:first)").remove();
		(this.context.customers || []).forEach((c) => {
			const label = c.customer_name || c.name;
			this.customerOptions.push({ value: c.name, label });
			$cust.append(
				`<option value="${frappe.utils.escape_html(c.name)}">${frappe.utils.escape_html(
					label
				)}</option>`
			);
		});
		if (currentCust) {
			$cust.val(currentCust);
			const match = this.customerOptions.find((o) => o.value === currentCust);
			this.$el.find("#sod-filter-customer-input").val(match ? match.label : "");
			this.$el.find("#sod-clear-customer-btn").addClass("visible");
		} else {
			this.$el.find("#sod-clear-customer-btn").removeClass("visible");
		}

		// 2. Projects
		this.projectOptions = [{ value: "", label: "All Projects" }];
		const $proj = this.$el.find("#sod-filter-project");
		const currentProj = $proj.val() || this.selectedProject;
		$proj.find("option:not(:first)").remove();
		(this.context.projects || []).forEach((p) => {
			const label = p.project_name || p.name;
			this.projectOptions.push({ value: p.name, label });
			$proj.append(
				`<option value="${frappe.utils.escape_html(p.name)}">${frappe.utils.escape_html(
					label
				)}</option>`
			);
		});
		if (currentProj && $proj.find(`option[value="${currentProj}"]`).length) {
			$proj.val(currentProj);
			const match = this.projectOptions.find((o) => o.value === currentProj);
			this.$el.find("#sod-filter-project-input").val(match ? match.label : "");
			this.$el.find("#sod-clear-project-btn").addClass("visible");
		} else if (currentProj) {
			$proj.val("");
			this.$el.find("#sod-filter-project-input").val("");
			this.$el.find("#sod-clear-project-btn").removeClass("visible");
		} else {
			this.$el.find("#sod-clear-project-btn").removeClass("visible");
		}
	}

	getFilters() {
		const custVal = this.$el.find("#sod-filter-customer").val();
		const custInputVal = this.$el.find("#sod-filter-customer-input").val();
		const projVal = this.$el.find("#sod-filter-project").val();
		const projInputVal = this.$el.find("#sod-filter-project-input").val();

		return {
			company: "",
			date_range: this.$el.find("#sod-filter-date").val() || "all",
			from_date: this.$el.find("#sod-filter-from-date").val() || "",
			to_date: this.$el.find("#sod-filter-to-date").val() || "",
			customer: custVal || (custInputVal ? custInputVal.trim() : ""),
			project: projVal || this.selectedProject || (projInputVal ? projInputVal.trim() : ""),
			status: this.$el.find("#sod-filter-status").val() || "",
			search: "",
			_ts: Date.now(),
		};
	}

	selectPage(idx) {
		this.currentPage = idx;
		this.$nav.find("button").removeClass("active");
		this.$nav.find(`button[data-page="${idx}"]`).addClass("active");

		const pageConfig = this.pagesConfig[idx] || [];
		const [title, , subtitle, , category] = pageConfig;

		// Dropdown state: If navigating to an Accounting & Finance module, auto-expand the dropdown
		const $accGroup = this.$nav.find("#sod-accounting-group");
		if (category === "ACCOUNTING & FINANCE") {
			this.accountingDropdownOpen = true;
			$accGroup.removeClass("collapsed").addClass("active-parent");
			$accGroup.find("#sod-accounting-toggle").attr("aria-expanded", "true");
		} else {
			$accGroup.removeClass("active-parent");
		}

		this.$el.attr("data-workspace", pageConfig[3]);
		this.$breadcrumb.text(title);
		this.$title.text(idx === 0 ? "Sarathi Owner Overview" : title);
		this.$subtitle.text(subtitle);

		this.refreshCurrentPage();
	}

	/* -------------------------------------------------------------
     DATA REFRESH: Full reload vs. Smooth Live Updating
  ------------------------------------------------------------- */
	setLiveStatus(ok) {
		if (ok) {
			this.lastSuccessfulRefresh = new Date();
			this.lastFailedRefresh = null;
			const timeStr = this.lastSuccessfulRefresh.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
			this.$el.find("#sod-live-status-text").text(`Last updated: ${timeStr}`);
			this.$content.find(".sui-stale-banner").remove();
		} else {
			this.lastFailedRefresh = new Date();
			if (this.activeData && Object.keys(this.activeData).length && this.lastSuccessfulRefresh) {
				const timeStr = this.lastSuccessfulRefresh.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
				this.$el.find("#sod-live-status-text").text(`Refresh failed · Showing data from ${timeStr}`);
				if (!this.$content.find(".sui-stale-banner").length) {
					this.$content.prepend(`
						<div class="sui-stale-banner" role="alert" style="margin-bottom:16px;">
							<p style="margin:0;">Refresh failed. Showing data from last successful update (${timeStr}).</p>
							<button type="button" class="sui-action" data-action="refresh" style="margin-left:auto;">Retry</button>
						</div>
					`);
				}
			} else {
				this.$el.find("#sod-live-status-text").text("Data unavailable");
				this.$content.html(
					'<div class="sod-empty" role="alert"><p>Live data could not be loaded. Please check your connection and try again.</p><button type="button" class="sui-action" data-action="refresh" style="margin-top:12px;">Retry</button></div>'
				);
			}
		}
	}

	refreshCurrentPage() {
        Object.values(this.chartResizeDisposers || {}).forEach(dispose => dispose());
        this.chartResizeDisposers = {};
		this.chartInstances = {};

		const formattedTime = this.lastSuccessfulRefresh ? this.lastSuccessfulRefresh.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : null;
		this.$el.find("#sod-live-status-text").text(formattedTime ? `Refreshing… (Last updated: ${formattedTime})` : "Refreshing…");

		this.$content.html(`
      <div class="sod-loading">
        <div class="sod-spinner"></div>
        <p>Connecting to ERPNext and aggregating real-time metrics…</p>
      </div>
    `);

		const request = (this.pageRequest = (this.pageRequest || 0) + 1);
		const pageIndex = this.currentPage;
		const filters = this.getFilters();
		const config = this.pagesConfig[this.currentPage] || this.pagesConfig[0];
		const pageKey = config[3] || "home";

		if (pageKey === "home") {
			frappe.call({
				method: "sarathi_owner.api.owner_dashboard.get_owner_summary",
				args: { filters: JSON.stringify(filters) },
				error: () => {
					if (request === this.pageRequest) this.setLiveStatus(false);
				},
				callback: (r) => {
					if (request !== this.pageRequest || pageIndex !== this.currentPage) return;
					this.setLiveStatus(Boolean(r.message));
					this.activeData = r.message || {};
					this.renderOwnerHome(this.activeData);
				},
			});
		} else if (pageKey === "reports") {
			this.renderReportsPage();
		} else {
			frappe.call({
				method: "sarathi_owner.api.owner_dashboard.get_page_data",
				args: {
					page_name: pageKey,
					filters: JSON.stringify(filters),
				},
				error: () => {
					if (request === this.pageRequest) this.setLiveStatus(false);
				},
				callback: (r) => {
					if (request !== this.pageRequest || pageIndex !== this.currentPage) return;
					this.setLiveStatus(Boolean(r.message));
					this.activeData = r.message || {};
					this.renderGenericPage(pageIndex, this.activeData);
				},
			});
		}
	}

	smoothRefresh() {
		const request = (this.pageRequest = (this.pageRequest || 0) + 1);
		const pageIndex = this.currentPage;
		const filters = this.getFilters();
		const config = this.pagesConfig[this.currentPage] || this.pagesConfig[0];
		const pageKey = config[3] || "home";

		const formattedTime = this.lastSuccessfulRefresh ? this.lastSuccessfulRefresh.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" }) : null;
		this.$el.find("#sod-live-status-text").text(formattedTime ? `Refreshing… (Last updated: ${formattedTime})` : "Refreshing…");

		if (pageKey === "home") {
			frappe.call({
				method: "sarathi_owner.api.owner_dashboard.get_owner_summary",
				args: { filters: JSON.stringify(filters) },
				error: () => {
					if (request === this.pageRequest) this.setLiveStatus(false);
				},
				callback: (r) => {
					if (request !== this.pageRequest || pageIndex !== this.currentPage) return;
					this.setLiveStatus(Boolean(r.message));
					if (!r.message) return;
					const oldData = this.activeData;
					this.activeData = r.message;
					this.updateOwnerHomeSmoothly(oldData, this.activeData);
				},
			});
		} else if (pageKey === "reports") {
			this.executeLiveReport(this.currentReportName, false);
		} else {
			frappe.call({
				method: "sarathi_owner.api.owner_dashboard.get_page_data",
				args: {
					page_name: pageKey,
					filters: JSON.stringify(filters),
				},
				error: () => {
					if (request === this.pageRequest) this.setLiveStatus(false);
				},
				callback: (r) => {
					if (request !== this.pageRequest || pageIndex !== this.currentPage) return;
					this.setLiveStatus(Boolean(r.message));
					if (!r.message) return;
					this.activeData = r.message;
					this.renderGenericPage(pageIndex, this.activeData);
				},
			});
		}
	}

	/* -------------------------------------------------------------
     RENDERER: Page 0 (Owner Home)
  ------------------------------------------------------------- */
	renderOwnerHome(data) {
        Object.values(this.chartResizeDisposers || {}).forEach(dispose => dispose());
        this.chartResizeDisposers = {};
		const cards = data.cards || [];
		const pipelines = data.pipelines || [];
		const alerts = data.action_alerts || [];
		const liveActivity = data.live_activity || [];
		const activeProjects = data.active_projects || [];
		const capital = data.capital_allocation || {};

		let html = "";

		// 1. KPI Cards (Executive Metrics)
		html += '<div class="sod-grid sod-cards" id="sod-kpi-cards-grid">';
		cards.forEach((c) => {
            const card = frappe.sarathiUI.kpi({ label: c.label, value: c.value, description: c.desc || "ERPNext records" });
            card.classList.add("sod-card");
            card.querySelector(".sui-kpi-label").classList.add("sod-label");
            card.querySelector(".sui-kpi-value").classList.add("sod-kpi-val");
            if (c.action) {
                // Existing bindEvents delegation owns the action; do not attach a second listener.
                card.dataset.action = c.action;
                card.setAttribute("role", "button"); card.tabIndex = 0;
                card.setAttribute("aria-label", c.label + ". View records");
            }
            html += card.outerHTML;
        });
		html += "</div>";

		// 2. Strategic Manufacturing Pipeline Section (Matrix Comparison Table Format - Steps 1–8)
		// Placed above Financial Health & Net Margin Run-Rate section
		html += `
      <section class="sod-panel sod-pipeline-sheet-section" style="margin-top: 17px;">
        <div class="sod-panel-head">
          <div>
            <h2>Strategic Manufacturing Pipeline · Active Projects</h2>
            <p>Commercial &amp; Sales Engineering Process Flow (Steps #01 to #08) · Complete (✔), Waiting (⏳) &amp; Not Done (✖) Status per Client · Click any mark to inspect live records</p>
          </div>
          <div>
            <span class="sod-sheet-count-pill">${pipelines.length} Active Clients Tracked</span>
          </div>
        </div>
        ${this.renderStrategicPipelineSheet(pipelines)}
      </section>
    `;

		// 2. Interactive Charts Grid (Frappe Charts)
		html += `
      <div class="sod-grid sod-two" style="margin-top: 17px;">
        <!-- Chart 1: Revenue vs Operating Expenses vs Net Profit -->
        <div class="sod-chart-card">
          <div class="sod-chart-card-head">
            <div>
              <h2>Financial Health & Net Margin Run-Rate</h2>
              <p>Monthly Invoiced Revenue, Direct Operating Costs, and Profit (6 Months)</p>
            </div>
            <div>
              <button class="sod-btn-sm" data-action="open-live-report" data-report="Profit and Loss Statement">Run P&L Report ⚡</button>
            </div>
          </div>
          <div id="sod-chart-financial" class="sod-chart-container"></div>
        </div>

        <!-- Chart 2: Working Capital Distribution Donut -->
        <div class="sod-chart-card">
          <div class="sod-chart-card-head">
            <div>
              <h2>Working Capital in Stock Valuation</h2>
              <p>Total Balance: <b>${capital.total_val || "₹0"}</b> · Asset Liquidity</p>
            </div>
            <div>
              <button class="sod-btn-sm" data-action="open-live-report" data-report="Warehouse Wise Stock Balance">Stock Report ⚡</button>
            </div>
          </div>
          <div id="sod-chart-capital" class="sod-chart-container"></div>
        </div>
      </div>
    `;

		// 3. Second Row of Interactive Charts (Order Book & Factory Output)
		html += `
      <div class="sod-grid sod-two" style="margin-top: 17px;">
        <!-- Chart 3: Order Book vs Delivery -->
        <div class="sod-chart-card">
          <div class="sod-chart-card-head">
            <div>
              <h2>Commercial Intake vs Fulfillment Velocity</h2>
              <p>Booked Sales Orders vs Dispatched Invoiced Value</p>
            </div>
            <div>
              <button class="sod-btn-sm" data-action="open-live-report" data-report="Sales Order Analysis">Order Analysis ⚡</button>
            </div>
          </div>
          <div id="sod-chart-orderbook" class="sod-chart-container"></div>
        </div>

        <!-- Chart 4: Accounts Receivable Aging Risk Breakdown -->
        <div class="sod-chart-card">
          <div class="sod-chart-card-head">
            <div>
              <h2>Accounts Receivable Aging Exposure</h2>
              <p>Overdue customer debts grouped by collection risk brackets</p>
            </div>
            <div>
              <button class="sod-btn-sm" data-action="open-live-report" data-report="Accounts Receivable">AR Aging Report ⚡</button>
            </div>
          </div>
          <div id="sod-chart-ar-aging" class="sod-chart-container"></div>
        </div>
      </div>
    `;

		// 3.5 Accounts & Financial Process Overview (Pooja Chougule - Step 9 & Step 24)
		const accts = data.accounts_flow || {};
		const adv = accts.advance_approvals || {};
		const doc = accts.documentation_invoicing || {};
		const fin = data.financial_snapshot || {};

		html += `
      <section class="sod-accounts-overview">
        <div class="sod-accounts-head">
          <div class="sod-accounts-title-block">
            <h2>🏛️ Accounts & Financial Operations · Process Flow</h2>
            <p>Direct governance of Step 9 (Advance Payment Approval) and Step 24 (Invoicing & Documentation) · In-Charge: <b>Pooja Chougule</b></p>
          </div>
          <div>
            <button class="sod-btn-sm" data-action="go-to-invoicing">Go to Accounting & Finance ↗</button>
          </div>
        </div>
        <div class="sod-accounts-grid">
          <!-- Card 1: Step 9 Advance Payment Approval -->
          <div class="sod-accounts-card" data-action="open-advance-orders" title="Click to view Sales Orders awaiting advance clearance">
            <div class="sod-accounts-card-header">
              <div>
                <span class="sod-accounts-step-badge">STEP 09 · ACCOUNTS CLEARANCE</span>
                <h3 style="font-size:14px; font-weight:800; color:#0f172a; margin:6px 0 2px;">Advance Payment Approval</h3>
                <span style="font-size:11px; color:#4f46e5; font-weight:700;">👤 In-Charge: Pooja Chougule</span>
              </div>
              <span class="sod-pill ${adv.pending_count > 0 ? "purple" : "green"}">${
			adv.pending_count > 0 ? "● ACTION REQUIRED" : "✓ ALL CLEARED"
		}</span>
            </div>
            <div class="sod-accounts-card-body">
              <div class="sod-accounts-metric-row">
                <span>Orders Awaiting Advance:</span>
                <span class="sod-accounts-metric-val" style="color:#ef4444;">${
					adv.pending_count || 0
				} Orders (${adv.pending_amount || "₹0"})</span>
              </div>
              <div class="sod-accounts-metric-row">
                <span>Total Advance Realized:</span>
                <span class="sod-accounts-metric-val" style="color:#10b981;">${
					adv.advance_received || "₹0"
				}</span>
              </div>
              <div class="sod-accounts-metric-row">
                <span>Active Open Order Book:</span>
                <span class="sod-accounts-metric-val">${adv.total_orders || 0} Orders</span>
              </div>
            </div>
          </div>

          <!-- Card 2: Step 24 Documentation & Invoicing -->
          <div class="sod-accounts-card" data-action="open-sales-invoices" title="Click to view Sales Invoices and Billing Ledger">
            <div class="sod-accounts-card-header">
              <div>
                <span class="sod-accounts-step-badge">STEP 24 · DOCUMENTATION & INVOICING</span>
                <h3 style="font-size:14px; font-weight:800; color:#0f172a; margin:6px 0 2px;">Documentation, E-Way & Invoicing</h3>
                <span style="font-size:11px; color:#4f46e5; font-weight:700;">👤 In-Charge: Pooja Chougule</span>
              </div>
              <span class="sod-pill ${fin.overdue && fin.overdue !== "₹0" ? "red" : "green"}">${
			fin.overdue && fin.overdue !== "₹0" ? "⚠ OVERDUE RISK" : "✓ HEALTHY"
		}</span>
            </div>
            <div class="sod-accounts-card-body">
              <div class="sod-accounts-metric-row">
                <span>Total Invoiced Revenue:</span>
                <span class="sod-accounts-metric-val" style="color:#2563eb;">${
					doc.total_invoiced || fin.income || "₹0"
				}</span>
              </div>
              <div class="sod-accounts-metric-row">
                <span>Outstanding Receivables:</span>
                <span class="sod-accounts-metric-val">${
					doc.outstanding_receivables || fin.receivables || "₹0"
				}</span>
              </div>
              <div class="sod-accounts-metric-row">
                <span>Overdue Receivables Alert:</span>
                <span class="sod-accounts-metric-val" style="color:#ef4444;">${
					doc.overdue_receivables || fin.overdue || "₹0"
				} (${doc.overdue_invoices_count || 0} Invoices)</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    `;

		// 3. Two-Column Grid: Active Projects Table & Live Activity Feed
		html += '<div class="sod-grid sod-two" style="margin-top: 17px;">';

		// Panel A: Active Projects Portfolio Table
		html += `
      <div class="sod-panel">
        <div class="sod-panel-head">
          <div>
            <h2>Active Manufacturing Projects Portfolio</h2>
            <p>Click any row to drill into Project Details; click links to view ERPNext docs</p>
          </div>
          <div>
            <button class="sod-btn-sm" data-action="view-projects">All Projects ↗</button>
          </div>
        </div>
        <div class="sod-tablewrap">
          <table class="sod-table">
            <thead>
              <tr><th>PROJECT</th><th>CUSTOMER</th><th>PROGRESS</th><th>BUDGET</th><th>ACTUAL COST</th><th>EXPECTED END</th><th>STATUS</th><th>DRILL</th></tr>
            </thead>
            <tbody>
    `;
		if (!activeProjects.length) {
			html +=
				'<tr><td colspan="8" style="text-align:center; color:#888;">No active projects recorded under current filters.</td></tr>';
		} else {
			activeProjects.forEach((row) => {
				const statusVal = row.status || "Open";
				const isHold = statusVal.toLowerCase() === "on hold" || statusVal.toLowerCase() === "hold";
				const isDone = statusVal.toLowerCase() === "completed";
				const isCancel = statusVal.toLowerCase() === "cancelled";
				const pillColor = isDone
					? "green"
					: isHold
					? "amber"
					: isCancel
					? "red"
					: row.schedule_status === "Delayed"
					? "amber"
					: "blue";
				html += `
          <tr class="sod-clickable-row" data-project-drill="${frappe.utils.escape_html(row.project)}">
            <td><a href="/app/project/${encodeURIComponent(
				row.project
			)}" target="_blank" class="sod-link">${frappe.utils.escape_html(row.project_name)}</a></td>
            <td><a href="/app/customer/${encodeURIComponent(
				row.customer
			)}" target="_blank" class="sod-link">${frappe.utils.escape_html(row.customer)}</a></td>
            <td><b>${row.percent_complete}%</b> <small style="color:#778899;">(${frappe.utils.escape_html(
					row.wo_output
				)})</small></td>
            <td>${frappe.utils.escape_html(row.budget)}</td>
            <td>${frappe.utils.escape_html(row.actual_cost)}</td>
            <td>${frappe.utils.escape_html(row.expected_end_date)}</td>
            <td><span class="sod-pill ${pillColor}">${frappe.utils.escape_html(statusVal)}</span>${
					row.schedule_status === "Delayed"
						? ' <small style="color:#ef4444;font-weight:700;">(Delayed)</small>'
						: ""
				}</td>
            <td><button class="sod-btn-sm" data-project-drill="${frappe.utils.escape_html(
				row.project
			)}" title="Drill into Project Details">View ▤</button></td>
          </tr>
        `;
			});
		}
		html += `
            </tbody>
          </table>
        </div>
      </div>
    `;

		// Panel B: Live Curated Activity Feed
		html += `
      <div class="sod-panel">
        <div class="sod-panel-head">
          <div>
            <h2>Recent Business Events <span class="sod-live-status-pill"><span class="sod-pulse-dot"></span> ERPNext records</span></h2>
            <p>Curated stream of Sales, Manufacturing, Invoicing, and Stock movements</p>
          </div>
          <div>
            <button class="sod-btn-sm" data-action="refresh" title="Sync live records">↻ Sync</button>
          </div>
        </div>
        <div class="sod-activity-list" id="sod-activity-feed-list">
    `;
		if (!liveActivity.length) {
			html +=
				'<div style="color:#7788a0; font-size:12px; padding:16px 0; text-align:center;">No recent business transactions recorded in ERPNext.</div>';
		} else {
			liveActivity.forEach((act) => {
				html += `
          <div class="sod-activity-item" data-route="${frappe.utils.escape_html(
				act.route || ""
			)}" title="Click to view document in Desk">
            <div class="sod-activity-icon ${act.badge_color || "blue"}">${act.icon || "✦"}</div>
            <div class="sod-activity-info">
              <div class="sod-activity-head">
                <span class="sod-activity-title">${frappe.utils.escape_html(act.title)}</span>
                <span class="sod-activity-time">${frappe.utils.escape_html(act.time_ago)}</span>
              </div>
              <div class="sod-activity-desc">${frappe.utils.escape_html(act.desc)}</div>
            </div>
            <span class="sod-card-arrow" style="position:static; margin-left:6px;">↗</span>
          </div>
        `;
			});
		}
		html += `
        </div>
      </div>
    `;
		html += "</div>";

		this.$content.html(html);
		this.bindPipelineClicks();

		// Render Native Frappe Charts
		this.renderHomeCharts(data.charts);
	}

	renderHomeCharts(charts) {
		if (!charts) return;

		// 1. Financial Chart (Revenue vs Expenses vs Profit)
		if (charts.financial) {
			this.renderFrappeChart("#sod-chart-financial", {
				data: charts.financial,
				type: "bar",
				colors: ["#5369ef", "#f06478", "#12b886"],
				barOptions: { spaceRatio: 0.25 },
			});
		}

		// 2. Working Capital Donut
		if (charts.capital) {
			this.renderFrappeChart("#sod-chart-capital", {
				data: charts.capital,
				type: "donut",
				colors: ["#5369ef", "#f2a342", "#12b886"],
			});
		}

		// 3. Order Book vs Fulfillment
		if (charts.order_book) {
			this.renderFrappeChart("#sod-chart-orderbook", {
				data: charts.order_book,
				type: "bar",
				colors: ["#15b9cf", "#12b886"],
				barOptions: { spaceRatio: 0.25 },
			});
		}

		// 4. Accounts Receivable Aging
		if (charts.ar_aging) {
			this.renderFrappeChart("#sod-chart-ar-aging", {
				data: charts.ar_aging,
				type: "bar",
				colors: ["#12b886", "#f2a342", "#e03131", "#c92a2a", "#a61e4d"],
				barOptions: { spaceRatio: 0.35 },
			});
		}
	}

	renderFrappeChart(selector, options) {
		const $target = this.$content.find(selector);
		if (!$target.length) return null;
        this.chartResizeDisposers?.[selector]?.();
		$target.empty();

		try {
			if (window.frappe && frappe.Chart) {
				const chart = new frappe.Chart($target[0], {
                    animate: false,
                    disableEntryAnimation: true,
					data: options.data || { labels: [], datasets: [] },
					type: options.type || "bar",
					height: options.height || 220,
					colors: options.colors || ["#5369ef", "#12b886", "#f2a342", "#e03131"],
					barOptions: options.barOptions || { spaceRatio: 0.3 },
					axisOptions: { xIsSeries: true },
					tooltipOptions: {
						formatTooltipX: (d) => (d + "").toUpperCase(),
						formatTooltipY: (d) => (typeof d === "number" ? "₹" + d.toLocaleString("en-IN") : d),
					},
				});
				this.chartResizeDisposers ||= {};
                this.chartResizeDisposers[selector]?.();
                this.chartResizeDisposers[selector] = frappe.sarathiUI.observeChart($target[0], chart);
                this.chartInstances[selector] = chart;
				return chart;
			}
		} catch (e) {
			console.warn("Chart render notice:", e);
		}
		return null;
	}

	updateOwnerHomeSmoothly(oldData, newData) {
		// 1. Update KPI Card numbers with subtle flash
		const $cards = this.$content.find("#sod-kpi-cards-grid .sod-card");
		(newData.cards || []).forEach((c, idx) => {
			const $card = $cards.eq(idx);
			if ($card.length) {
				const $strong = $card.find(".sod-kpi-val");
				if ($strong.text().trim() !== (c.value || "").trim()) {
					$strong.text(c.value);
					$strong.addClass("sod-value-updated");
					setTimeout(() => $strong.removeClass("sod-value-updated"), 1200);
				}
			}
		});

		// 2. Update Charts
		if (newData.charts) {
			if (this.chartInstances["#sod-chart-financial"] && newData.charts.financial) {
				this.chartInstances["#sod-chart-financial"].update(newData.charts.financial);
			}
			if (this.chartInstances["#sod-chart-capital"] && newData.charts.capital) {
				this.chartInstances["#sod-chart-capital"].update(newData.charts.capital);
			}
			if (this.chartInstances["#sod-chart-orderbook"] && newData.charts.order_book) {
				this.chartInstances["#sod-chart-orderbook"].update(newData.charts.order_book);
			}
			if (this.chartInstances["#sod-chart-ar-aging"] && newData.charts.ar_aging) {
				this.chartInstances["#sod-chart-ar-aging"].update(newData.charts.ar_aging);
			}
		}
	}

	/* -------------------------------------------------------------
     RENDERER: Page 8 (In-Tower Live Report Runner)
  ------------------------------------------------------------- */
	renderReportsPage() {
		const reportOptions = [
			[
				"Accounts Receivable",
				"Customer unpaid invoice aging, overdue balances, and debt risks",
				"Finance",
				"₹",
			],
			[
				"Profit and Loss Statement",
				"Official P&L statement: revenue vs operating expenses and net margin",
				"Finance",
				"📈",
			],
			[
				"Gross and Net Profit Report",
				"Direct production costs, gross margin %, and business profit",
				"Finance",
				"⚖",
			],
			[
				"Sales Order Analysis",
				"Commercial intake vs delivery backlog and pending fulfillment",
				"Commercial",
				"▣",
			],
			["Warehouse Wise Stock Balance", "Working capital valuation across warehouses", "Stock", "◫"],
			[
				"Production Analytics",
				"Factory output volume and monthly completion velocity",
				"Manufacturing",
				"⚙",
			],
			[
				"Work Order Summary",
				"Work orders status, planned vs produced quantities and cycle age",
				"Manufacturing",
				"🏭",
			],
			[
				"Project Summary",
				"Project costing margins: budget vs actual costs and milestone health",
				"Projects",
				"▦",
			],
		];

		let html = `
      <div class="sod-report-runner">
        <!-- Report Header Bar -->
        <div class="sod-report-header">
          <div class="sod-report-title-group">
            <h2 id="sod-live-report-title">
              <span id="sod-report-icon">₹</span>
              <span id="sod-report-name-text">${frappe.utils.escape_html(this.currentReportName)}</span>
              <span class="sod-pill green">LIVE EMBEDDED</span>
            </h2>
            <p id="sod-report-desc-text">Official native ERPNext report running live inside Sarathi Owner Control Tower</p>
          </div>
          <div class="sod-report-controls">
            <select id="sod-report-switcher" class="sod-select" style="font-weight:700; max-width:250px;">
    `;

		reportOptions.forEach(([name, desc, type, icon]) => {
			const selected = name === this.currentReportName ? "selected" : "";
			html += `<option value="${frappe.utils.escape_html(
				name
			)}" data-icon="${icon}" data-desc="${frappe.utils.escape_html(
				desc
			)}" ${selected}>${icon} ${frappe.utils.escape_html(name)} (${type})</option>`;
		});

		html += `
            </select>
            <input type="search" id="sod-report-search" class="sod-input" placeholder="Filter rows in report..." style="width: 160px; max-width: 100%;">
            <button class="sod-btn-sm" id="sod-btn-refresh-report" title="Rerun report query">↻ Run Live</button>
            <button class="sod-btn-sm" id="sod-btn-export-csv" title="Download CSV of current table">⬇ Export CSV</button>
          </div>
        </div>

        <!-- Summary KPIs Bar -->
        <div id="sod-report-summary-container" class="sod-report-summary-bar"></div>

        <!-- Live Report Datatable Container -->
        <div class="sod-report-tablewrap">
          <div id="sod-report-table-area">
            <div class="sod-loading">
              <div class="sod-spinner"></div>
              <p>Executing live ERPNext report engine…</p>
            </div>
          </div>
        </div>

        <!-- Report Footer Meta -->
        <div class="sod-report-meta">
          <span id="sod-report-row-count">Loading records…</span>
          <span id="sod-report-exec-time"></span>
        </div>
      </div>
    `;

		this.$content.html(html);
		this.bindReportRunnerEvents();
		this.executeLiveReport(this.currentReportName, true);
	}

	bindReportRunnerEvents() {
		const self = this;

		// Report Switcher Dropdown
		this.$content.find("#sod-report-switcher").on("change", function () {
			const selectedReport = $(this).val();
			const $opt = $(this).find(":selected");
			self.currentReportName = selectedReport;
			self.$content.find("#sod-report-name-text").text(selectedReport);
			self.$content.find("#sod-report-icon").text($opt.data("icon") || "▥");
			self.$content.find("#sod-report-desc-text").text($opt.data("desc") || "Official ERPNext report");
			self.executeLiveReport(selectedReport, true);
		});

		// Refresh Button
		this.$content.find("#sod-btn-refresh-report").on("click", function () {
			self.executeLiveReport(self.currentReportName, true);
		});

		// Instant Search / Filter Rows
		this.$content.find("#sod-report-search").on("input", function () {
			self.reportSearchQuery = ($(this).val() || "").trim().toLowerCase();
			self.filterReportRows();
		});

		// Export to CSV
		this.$content.find("#sod-btn-export-csv").on("click", function () {
			self.exportReportToCSV();
		});
	}

	executeLiveReport(reportName, showSpinner) {
		const self = this;
		const filters = this.getFilters();
		const request = (this.reportRequest = (this.reportRequest || 0) + 1);
		const pageIndex = this.currentPage;

		if (showSpinner) {
			this.$content.find("#sod-report-table-area").html(`
        <div class="sod-loading">
          <div class="sod-spinner"></div>
          <p>Running live ${frappe.utils.escape_html(reportName)} query…</p>
        </div>
      `);
		}

		frappe.call({
			method: "sarathi_owner.api.owner_dashboard.get_live_report_data",
			args: {
				report_name: reportName,
				filters: JSON.stringify(filters),
			},
			callback: (r) => {
				if (
					request !== self.reportRequest ||
					pageIndex !== self.currentPage ||
					reportName !== self.currentReportName
				)
					return;
				if (r.message) {
					self.activeReportData = r.message;
					self.renderLiveReportTable(r.message);
				}
			},
			error: (err) => {
				if (request !== self.reportRequest || pageIndex !== self.currentPage) return;
				if (self.activeReportData && self.activeReportData.columns && self.activeReportData.columns.length) {
					if (!self.$content.find(".sui-stale-banner").length) {
						self.$content.find("#sod-report-table-area").prepend(`
							<div class="sui-stale-banner" role="alert" style="margin-bottom:12px;">
								<p style="margin:0;">Report refresh failed. Showing previously retrieved data.</p>
								<button type="button" class="sui-action" id="sod-btn-retry-report" style="margin-left:auto;">Retry</button>
							</div>
						`);
						self.$content.find("#sod-btn-retry-report").on("click", () => self.executeLiveReport(self.currentReportName, true));
					}
				} else {
					self.$content.find("#sod-report-table-area").html(`
						<div class="sod-empty" role="alert" style="color:#b91c1c;">
							<p style="margin:0 0 10px;">Unable to execute report query. Please verify your permissions and try again.</p>
							<button type="button" class="sui-action" id="sod-btn-retry-report">Retry</button>
						</div>
					`);
					self.$content.find("#sod-btn-retry-report").on("click", () => self.executeLiveReport(self.currentReportName, true));
				}
			},
		});
	}

	renderLiveReportTable(reportData) {
		const columns = reportData.columns || [];
		const rawResult = reportData.result || [];
		const summary = reportData.report_summary || [];
		const execTime = reportData.execution_time ? `${reportData.execution_time.toFixed(2)}s` : "";

		// 1. Render Summary Bar
		const $summaryContainer = this.$content.find("#sod-report-summary-container");
		$summaryContainer.empty();
		if (summary.length) {
			summary.forEach((kpi) => {
				const numVal = typeof flt !== "undefined" ? flt(kpi.value) : Number(kpi.value) || 0;
				let valFormatted = "";
				if (kpi.datatype === "Currency") {
					valFormatted =
						"₹" +
						numVal.toLocaleString("en-IN", {
							minimumFractionDigits: 2,
							maximumFractionDigits: 2,
						});
				} else if (kpi.datatype === "Percent") {
					valFormatted = numVal + "%";
				} else {
					valFormatted = String(kpi.value !== null && kpi.value !== undefined ? kpi.value : "");
				}

				$summaryContainer.append(`
          <div class="sod-report-kpi">
            <small>${frappe.utils.escape_html(kpi.label || "")}</small>
            <strong>${frappe.utils.escape_html(valFormatted)}</strong>
          </div>
        `);
			});
		}

		// 2. Normalize Rows (Handle list of dicts vs list of lists)
		const rows = [];
		rawResult.forEach((item) => {
			if (Array.isArray(item)) {
				rows.push(item);
			} else if (typeof item === "object" && item !== null) {
				const row = columns.map((col) => {
					const field = col.fieldname || col.label;
					return item[field] !== undefined ? item[field] : "";
				});
				rows.push(row);
			}
		});

		this.activeReportRows = rows;

		let tableHtml = `
      <table class="sod-report-table" id="sod-report-rendered-table">
        <thead>
          <tr>
    `;

		columns.forEach((c) => {
			tableHtml += `<th>${frappe.utils.escape_html(c.label || c.fieldname)}</th>`;
		});
		tableHtml += `
          </tr>
        </thead>
        <tbody>
    `;

		if (!rows.length) {
			tableHtml += `<tr><td colspan="${
				columns.length || 1
			}" style="text-align:center; padding: 24px; color:#8899aa;">No records returned for current company and date filters.</td></tr>`;
		} else {
			rows.forEach((r) => {
				tableHtml += "<tr>";
				r.forEach((cell, ci) => {
					const colDef = columns[ci] || {};
					let val = cell !== null && cell !== undefined ? cell : "";
					let formatted = val;

					if (colDef.fieldtype === "Currency" && typeof val === "number") {
						const numVal = typeof flt !== "undefined" ? flt(val) : Number(val) || 0;
						formatted =
							"₹" +
							numVal.toLocaleString("en-IN", {
								minimumFractionDigits: 2,
								maximumFractionDigits: 2,
							});
					} else if (colDef.fieldtype === "Date" && val) {
						formatted = String(val);
					} else if (colDef.fieldtype === "Link" && val && colDef.options) {
						const dtSlug = (colDef.options + "").toLowerCase().replace(/ /g, "-");
						formatted = `<a href="/app/${dtSlug}/${encodeURIComponent(
							val
						)}" target="_blank" class="sod-link">${frappe.utils.escape_html(String(val))}</a>`;
					} else {
						formatted = frappe.utils.escape_html(String(val));
					}

					tableHtml += `<td>${formatted}</td>`;
				});
				tableHtml += "</tr>";
			});
		}

		tableHtml += `
        </tbody>
      </table>
    `;

		this.$content.find("#sod-report-table-area").html(tableHtml);
		this.$content.find("#sod-report-row-count").text(`Total Rows: ${rows.length}`);
		this.$content.find("#sod-report-exec-time").text(execTime ? `Executed in ${execTime}` : "");
	}

	filterReportRows() {
		const q = this.reportSearchQuery;
		const $tbody = this.$content.find("#sod-report-rendered-table tbody");
		if (!$tbody.length) return;

		let matched = 0;
		$tbody.find("tr").each(function () {
			const text = $(this).text().toLowerCase();
			if (!q || text.includes(q)) {
				$(this).show();
				matched++;
			} else {
				$(this).hide();
			}
		});

		this.$content
			.find("#sod-report-row-count")
			.text(
				q ? `Showing ${matched} matching rows` : `Total Rows: ${this.activeReportRows?.length || 0}`
			);
	}

	exportReportToCSV() {
		if (!this.activeReportData || !this.activeReportData.columns) {
			frappe.show_alert({
				message: "No report data available to export",
				indicator: "orange",
			});
			return;
		}

		const cols = this.activeReportData.columns.map(
			(c) => `"${(c.label || c.fieldname).replace(/"/g, '""')}"`
		);
		const csvRows = [cols.join(",")];

		(this.activeReportRows || []).forEach((row) => {
			const escapedRow = row.map((cell) => {
				const strVal = cell !== null && cell !== undefined ? cell + "" : "";
				return `"${strVal.replace(/"/g, '""')}"`;
			});
			csvRows.push(escapedRow.join(","));
		});

		const csvContent = "data:text/csv;charset=utf-8," + encodeURIComponent(csvRows.join("\n"));
		const downloadAnchor = document.createElement("a");
		downloadAnchor.setAttribute("href", csvContent);
		downloadAnchor.setAttribute(
			"download",
			`${this.currentReportName.toLowerCase().replace(/ /g, "_")}_${frappe.datetime.now_date()}.csv`
		);
		document.body.appendChild(downloadAnchor);
		downloadAnchor.click();
		downloadAnchor.remove();

		frappe.show_alert({
			message: "CSV exported successfully",
			indicator: "green",
		});
	}

	slugifyDoctype(text) {
		if (!text) return "";
		return String(text)
			.toLowerCase()
			.trim()
			.replace(/[^a-z0-9]+/g, "-")
			.replace(/^-+|-+$/g, "");
	}

	/* -------------------------------------------------------------
     RENDERER: Generic Pages 1 to 7
  ------------------------------------------------------------- */
	renderGenericPage(pageIndex, data) {
		let html = "";
		const pageConfig = this.pagesConfig[pageIndex] || [];
		const pageKey = pageConfig[3] || "";

		// 1. Clickable KPI Cards
		if (data.cards && data.cards.length) {
			html += '<div class="sod-grid sod-cards">';
			data.cards.forEach(([label, value, color, desc, route]) => {
				html += `
          <div class="sod-card ${color}" data-action="open-desk" data-route="${frappe.utils.escape_html(
					route || ""
				)}" role="button" tabindex="0" title="Click to view in Desk">
            <div class="sod-label"><span class="sod-metric-icon">${this.workspaceIcon(
				label
			)}</span>${frappe.utils.escape_html(label)}</div>
            <strong class="sod-kpi-val">${frappe.utils.escape_html(value)}</strong>
            <small>${frappe.utils.escape_html(desc || "Open ERPNext list ↗")}</small>
            <span class="sod-card-arrow">↗</span>
          </div>
        `;
			});
			html += "</div>";
		}

		// 2. Interactive Charts on Specific Pages
		if (data.chart) {
			const chartTitles = {
				sales_orders: "Commercial Order Book Velocity",
				manufacturing: "Production Yield Velocity",
				invoicing: "Accounts Receivable Aging Schedule",
				finance: "Accounts Receivable Aging Schedule",
			};
			const title = chartTitles[pageKey] || "Analytical Trend Chart";
			html += `
        <div class="sod-chart-card" style="margin-top: 17px;">
          <div class="sod-chart-card-head">
            <div>
              <h2>${title}</h2>
              <p>Real-time records from native ERPNext transactional database</p>
            </div>
          </div>
          <div id="sod-generic-chart" class="sod-chart-container"></div>
        </div>
      `;
		}

		// 3. Data Tables with Linked Records (Rendered at top directly below filters/cards/charts)
		if (data.table && data.table.headers && data.table.rows) {
			html += `
        <div class="sod-panel" style="margin-top: 17px;">
          <div class="sod-tablewrap">
            <table class="sod-table">
              <thead>
                <tr>${data.table.headers.map((h) => `<th>${frappe.utils.escape_html(h)}</th>`).join("")}</tr>
              </thead>
              <tbody>
      `;
			if (!data.table.rows.length) {
				html += `<tr><td colspan="${data.table.headers.length}" style="text-align:center; color:#888;">No records found matching current filters.</td></tr>`;
			} else {
				data.table.rows.forEach((r) => {
					html += "<tr>";
					r.forEach((cell, ci) => {
						const strCell = String(cell !== null && cell !== undefined ? cell : "");

						// Pre-rendered HTML (links, buttons, pills)
						if (
							strCell.includes("<a ") ||
							strCell.includes("<span ") ||
							strCell.includes("<button ")
						) {
							html += `<td>${strCell}</td>`;
							return;
						}

						// Linkify based on pageKey
						if (pageKey === "projects" && ci === 0) {
							html += `<td><a href="/app/project/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "projects" && ci === 1) {
							const projId = r[0];
							html += `<td><a href="javascript:void(0)" data-project-drill="${encodeURIComponent(
								projId
							)}" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
						} else if (pageKey === "projects" && ci === 2 && strCell !== "Unassigned") {
							html += `<td><a href="/app/customer/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "projects" && ci === 3 && strCell !== "—") {
							html += `<td><a href="/app/sales-order/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "customers" && (ci === 0 || ci === 1)) {
							const custId = r[0];
							html += `<td><a href="/app/customer/${encodeURIComponent(
								custId
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "sales_orders" && ci === 0) {
							html += `<td><a href="/app/sales-order/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "sales_orders" && ci === 1) {
							html += `<td><a href="/app/customer/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "manufacturing" && ci === 0) {
							html += `<td><a href="/app/work-order/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "stock_quality" && (ci === 0 || ci === 1)) {
							const whId = r[0];
							html += `<td><a href="/app/warehouse/${encodeURIComponent(
								whId
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if ((pageKey === "invoicing" || pageKey === "finance") && ci === 0) {
							const isPurchase =
								strCell.toUpperCase().startsWith("PINV") ||
								strCell.toUpperCase().startsWith("PUR-");
							const dt = isPurchase ? "purchase-invoice" : "sales-invoice";
							html += `<td><a href="/app/${dt}/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if ((pageKey === "invoicing" || pageKey === "finance") && ci === 1) {
							html += `<td><a href="/app/customer/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "payments" && ci === 0) {
							html += `<td><a href="/app/payment-entry/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "taxes" && ci === 0) {
							html += `<td><a href="/app/sales-taxes-and-charges-template/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "banking" && ci === 0) {
							html += `<td><a href="/app/bank-account/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "budget" && ci === 0) {
							html += `<td><a href="/app/budget/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "share_management" && ci === 0) {
							html += `<td><a href="/app/shareholder/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (pageKey === "subscription" && ci === 0) {
							html += `<td><a href="/app/subscription/${encodeURIComponent(
								strCell
							)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
								strCell
							)}</a></td>`;
						} else if (
							strCell === "Delayed" ||
							strCell === "Stop" ||
							strCell === "Disabled" ||
							strCell.startsWith("Critical")
						) {
							html += `<td><span class="sod-pill red">${frappe.utils.escape_html(
								strCell
							)}</span></td>`;
						} else if (
							strCell === "On Track" ||
							strCell === "On Time" ||
							strCell === "Paid" ||
							strCell === "Active" ||
							strCell === "Registered" ||
							strCell === "Submitted" ||
							strCell === "Compliant" ||
							strCell === "Primary Default"
						) {
							html += `<td style="color:#0d825f; font-weight:700;"><span class="sod-pill green">${strCell}</span></td>`;
						} else if (strCell.startsWith("Overdue >30d")) {
							html += `<td><span class="sod-pill red">${frappe.utils.escape_html(
								strCell
							)}</span></td>`;
						} else if (
							strCell.startsWith("Overdue 1-30d") ||
							strCell === "Optional" ||
							strCell === "Warn"
						) {
							html += `<td><span class="sod-pill amber">${frappe.utils.escape_html(
								strCell
							)}</span></td>`;
						} else if (
							strCell === "Current (Not Due)" ||
							strCell === "Open" ||
							strCell === "Draft" ||
							strCell === "Receive" ||
							strCell === "Pay"
						) {
							html += `<td><span class="sod-pill blue">${frappe.utils.escape_html(
								strCell
							)}</span></td>`;
						} else {
							html += `<td>${frappe.utils.escape_html(strCell)}</td>`;
						}
					});
					html += "</tr>";
				});
			}
			html += `
              </tbody>
            </table>
          </div>
        </div>
      `;
		}

		// 4. Project Detail View (Page 2)
		if (pageKey === "project_detail") {
			if (data.empty || !data.project_fields) {
				html += `
          <div class="sod-panel" style="text-align: center; padding: 50px 24px; margin-top: 17px;">
            <div style="font-size: 52px; margin-bottom: 14px; color: #5369ef;">▦</div>
            <h2 style="font-size: 20px; font-weight: 700; margin-bottom: 8px; color: #17233f;">No Project Found in ERPNext</h2>
            <p style="color: #7583a0; max-width: 540px; margin: 0 auto 24px; font-size: 13px; line-height: 1.6;">
              ${frappe.utils.escape_html(
					data.description ||
						"There are no projects matching your filter in ERPNext. Create a new Project in ERPNext Desk to view its real-time 5-stage manufacturing pipeline, budget vs actual financials, and milestone deliverables."
				)}
            </p>
            <div style="display: flex; justify-content: center; gap: 12px; flex-wrap: wrap;">
              <button class="sod-btn-sm" style="background:#5369ef; color:#fff; border:none; padding: 9px 20px; font-size: 13px; font-weight: 600; border-radius: 6px; cursor:pointer;" onclick="frappe.set_route('sarathiownertower')">Go to Owner Overview</button>
            </div>
          </div>
        `;
				this.$content.html(html);
				return;
			}

			// Sync top filter dropdown with selected project
			if (data.selected_project) {
				this.selectedProject = data.selected_project;
				const $topProj = this.$el.find("#sod-filter-project");
				if ($topProj.find(`option[value="${data.selected_project}"]`).length) {
					$topProj.val(data.selected_project);
				}
			}

			const allProjects = data.all_projects || [];
			const pf = data.project_fields;

			// In-Page Project Switcher & Header Bar
			html += `
        <div class="sod-panel" style="margin-top: 14px; padding: 16px 20px;">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 14px;">
            <div>
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 4px;">
                <span style="font-size: 18px; font-weight: 700; color: #17233f;">${frappe.utils.escape_html(
					pf.project_name || pf.name
				)}</span>
                <span class="sod-pill ${
					pf.status === "Completed"
						? "green"
						: (pf.status || "").toLowerCase().includes("hold")
						? "amber"
						: pf.status === "Cancelled"
						? "red"
						: "blue"
				}">${frappe.utils.escape_html(pf.status || "Open")}</span>
              </div>
              <p style="margin: 0; color: #7583a0; font-size: 12px;">
                ID: <a href="/app/project/${encodeURIComponent(
					pf.name
				)}" target="_blank" class="sod-link"><b>${frappe.utils.escape_html(pf.name)}</b></a> ·
                Customer: <b>${frappe.utils.escape_html(pf.customer || "Unassigned")}</b> ·
                Company: <b>${frappe.utils.escape_html(pf.company || "—")}</b> ·
                Delivery: <b>${frappe.utils.escape_html(pf.expected_end_date || "—")}</b>
              </p>
            </div>
            <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
              ${
					allProjects.length > 1
						? `
                <div style="display: flex; align-items: center; gap: 6px;">
                  <label style="font-size: 12px; font-weight: 600; color: #64748b;">Switch Project:</label>
                  <select id="sod-inpage-project-select" class="sod-select" style="padding: 6px 12px; font-size: 12px; font-weight: 500; border-radius: 6px; border: 1px solid #cbd5e1; background: #fff;">
                    ${allProjects
						.map(
							(p) => `
                      <option value="${frappe.utils.escape_html(p.name)}" ${
								p.name === data.selected_project ? "selected" : ""
							}>
                        ${frappe.utils.escape_html(p.project_name || p.name)}
                      </option>
                    `
						)
						.join("")}
                  </select>
                </div>
              `
						: ""
				}
            </div>
          </div>
        </div>
      `;

			// Visual Manufacturing & Delivery Pipeline Matrix (Steps 9–24)
			if (this.isManufacturingPipelineReady(data.pipeline)) {
				html += `
          <section class="sod-panel sod-pipeline-sheet-section" style="margin-top: 17px;">
            <div class="sod-panel-head">
              <div>
                <h2>Manufacturing &amp; Delivery Pipeline</h2>
                <p>Real-time lifecycle tracking across BOM, Production, Work Orders, and Manufactured Stock (Steps 9–24)</p>
              </div>
              <div style="font-size: 12px; color: #7583a0;">
                Milestone: <b>${data.pipeline.percent_complete}%</b> · Factory Yield: <b>${
					data.pipeline.manufacturing_progress
				}%</b>
              </div>
            </div>
            ${this.renderManufacturingDeliverySheet([data.pipeline])}
          </section>
        `;
			}

			// Financial Margins & Milestone Tasks Grid
			html += `
        <div class="sod-grid sod-two" style="margin-top: 17px;">
          <div class="sod-panel">
            <div class="sod-panel-head">
              <div>
                <h2>Project Financial Margins</h2>
                <p>Budget vs actual costs and billing realization</p>
              </div>
            </div>
            <div class="sod-feed"><b>Estimated Budget:</b> <span>${pf.estimated_cost}</span></div>
            <div class="sod-feed"><b>Actual Cost Incurred:</b> <span>${pf.actual_cost}</span></div>
            <div class="sod-feed"><b>Cost Variance:</b> <span>${pf.cost_variance}</span></div>
            <div class="sod-feed"><b>Total Billed:</b> <span>${pf.total_billed}</span></div>
            <div class="sod-feed"><b>Net Margin Realized:</b> <span style="color:#12b886; font-weight:700;">${pf.margin}</span></div>
          </div>
          <div class="sod-panel">
            <div class="sod-panel-head">
              <div>
                <h2>Milestone Tasks & Deadlines</h2>
                <p>Critical path deliverables</p>
              </div>
            </div>
            <div class="sod-tablewrap">
              <table class="sod-table">
                <thead><tr><th>TASK</th><th>STATUS</th><th>DUE DATE</th></tr></thead>
                <tbody>
      `;
			if (!data.tasks || !data.tasks.length) {
				html += `<tr><td colspan="3" style="text-align:center; color:#888;">No tasks created for this project yet.</td></tr>`;
			} else {
				(data.tasks || []).forEach((t) => {
					html += `<tr><td><a href="/app/task/${encodeURIComponent(
						t.task_id || t.task
					)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
						t.task
					)}</a></td><td><span class="sod-pill ${t.status === "Completed" ? "green" : "blue"}">${
						t.status
					}</span></td><td>${frappe.utils.escape_html(t.date || "—")}</td></tr>`;
				});
			}
			html += `
                </tbody>
              </table>
            </div>
          </div>
        </div>
      `;

			// Linked Sales Orders Table
			if (data.sales_orders && data.sales_orders.length) {
				html += `
          <div class="sod-panel" style="margin-top: 17px;">
            <div class="sod-panel-head">
              <div>
                <h2>Linked Commercial Sales Orders</h2>
                <p>Customer orders linked to this project</p>
              </div>
            </div>
            <div class="sod-tablewrap">
              <table class="sod-table">
                <thead><tr><th>ORDER ID</th><th>CUSTOMER</th><th>AMOUNT</th><th>% DELIVERED</th><th>% BILLED</th><th>PROMISED DELIVERY</th><th>STATUS</th></tr></thead>
                <tbody>
        `;
				data.sales_orders.forEach((r) => {
					html += `<tr><td><a href="/app/sales-order/${encodeURIComponent(
						r[0]
					)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
						r[0]
					)}</a></td><td>${frappe.utils.escape_html(r[1])}</td><td>${frappe.utils.escape_html(
						r[2]
					)}</td><td>${frappe.utils.escape_html(r[3])}</td><td>${frappe.utils.escape_html(
						r[4]
					)}</td><td>${frappe.utils.escape_html(
						r[5]
					)}</td><td><span class="sod-pill blue">${frappe.utils.escape_html(
						r[6]
					)}</span></td></tr>`;
				});
				html += `</tbody></table></div></div>`;
			}

			// Linked Work Orders Table
			if (data.work_orders && data.work_orders.length) {
				html += `
          <div class="sod-panel" style="margin-top: 17px;">
            <div class="sod-panel-head">
              <div>
                <h2>Linked Factory Work Orders</h2>
                <p>Shop-floor production jobs for this project</p>
              </div>
            </div>
            <div class="sod-tablewrap">
              <table class="sod-table">
                <thead><tr><th>WORK ORDER</th><th>PRODUCTION ITEM</th><th>PLANNED QTY</th><th>PRODUCED QTY</th><th>YIELD PROGRESS</th><th>PLANNED END</th><th>STATUS</th></tr></thead>
                <tbody>
        `;
				data.work_orders.forEach((r) => {
					html += `<tr><td><a href="/app/work-order/${encodeURIComponent(
						r[0]
					)}" target="_blank" class="sod-link">${frappe.utils.escape_html(
						r[0]
					)}</a></td><td>${frappe.utils.escape_html(r[1])}</td><td>${frappe.utils.escape_html(
						r[2]
					)}</td><td>${frappe.utils.escape_html(r[3])}</td><td>${frappe.utils.escape_html(
						r[4]
					)}</td><td>${frappe.utils.escape_html(r[5])}</td><td><span class="sod-pill ${
						r[6] === "Completed" ? "green" : "purple"
					}">${frappe.utils.escape_html(r[6])}</span></td></tr>`;
				});
				html += `</tbody></table></div></div>`;
			}
		}

		// 4.5. Categorized Module Sections & Operations (Rendered directly inside the dashboard)
		if (data.sections && data.sections.length) {
			let totalSectionItems = 0;
			data.sections.forEach((s) => {
				totalSectionItems += (s.items || []).length;
			});

			const kindStyles = {
				doctype: "background: #dbeafe; color: #1e40af; border: 1px solid #bfdbfe;",
				report: "background: #fef3c7; color: #92400e; border: 1px solid #fde68a;",
				workspace: "background: #ede9fe; color: #5b21b6; border: 1px solid #ddd6fe;",
				dashboard: "background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0;",
			};

			html += `
        <div class="sod-sections-container" style="margin: 20px 0; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 16px; padding: 22px 24px; box-shadow: 0 2px 10px rgba(15,23,42,0.03);">
          <div class="sod-sections-header" style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 20px; padding-bottom: 14px; border-bottom: 1px solid #e2e8f0; gap: 14px; flex-wrap: wrap;">
            <div class="sod-sections-header-left">
              <span class="sod-sections-kicker" style="font-size: 11px; font-weight: 800; letter-spacing: 1.2px; text-transform: uppercase; color: #4f46e5; display: block; margin-bottom: 4px;">MODULE SECTIONS & WORKSPACES</span>
              <h3 class="sod-sections-title" style="font-size: 19px; font-weight: 700; color: #0f172a; margin: 0;">${frappe.utils.escape_html(
					pageConfig[0] || "Module"
				)} Nested Sections & Records</h3>
            </div>
            <div class="sod-sections-header-right">
              <span class="sod-sections-count-pill" style="background: #ffffff; border: 1px solid #cbd5e1; border-radius: 20px; padding: 5px 14px; font-size: 12px; font-weight: 600; color: #475569; box-shadow: 0 1px 3px rgba(0,0,0,0.04); white-space: nowrap;">${totalSectionItems} items · ${
				data.sections.length
			} sections</span>
            </div>
          </div>
          <div class="sod-sections-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(350px, 1fr)); gap: 18px;">
      `;

			data.sections.forEach((sec, sIdx) => {
				const items = sec.items || [];
				if (!items.length) return;
				html += `
          <div class="sod-section-box" style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px 18px; box-shadow: 0 2px 6px rgba(15, 23, 42, 0.04); display: flex; flex-direction: column;">
            <div class="sod-section-box-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid #f1f5f9;">
              <div class="sod-section-box-title-wrap" style="display: flex; align-items: center; gap: 10px;">
                <span class="sod-section-box-icon" style="width: 28px; height: 28px; border-radius: 7px; background: #eef2ff; color: #4f46e5; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;">${this.workspaceIcon(
					sec.title
				)}</span>
                <h4 class="sod-section-box-title" style="font-size: 15px; font-weight: 700; color: #0f172a; margin: 0;">${frappe.utils.escape_html(
					sec.title
				)}</h4>
              </div>
              <span class="sod-section-box-badge" style="background: #f1f5f9; color: #475569; font-size: 11px; font-weight: 700; padding: 3px 9px; border-radius: 12px; border: 1px solid #e2e8f0;">${
					items.length
				}</span>
            </div>
            <div class="sod-section-items-grid" style="display: flex; flex-direction: column; gap: 8px;">
        `;

				items.forEach((item, iIdx) => {
					const kind = item.kind || "DocType";
					const kindLower = kind.toLowerCase();
					const route = item.route || `/app/${this.slugifyDoctype(item.target || item.label)}`;
					const deskRoute = route.startsWith("/desk/")
						? route.replace(/^\/desk\//, "/app/")
						: route;
					const isDocType = kind === "DocType" && !item.is_single;
					const targetSlug = this.slugifyDoctype(item.target || item.label);
					const kStyle = kindStyles[kindLower] || kindStyles.doctype;

					html += `
            <div class="sod-module-item-card" data-section-quick="${sIdx}_${iIdx}" role="button" tabindex="0" title="Click to view live calculations, graphs & details for ${frappe.utils.escape_html(
						item.label
					)}" style="display: flex; justify-content: space-between; align-items: center; background: #ffffff; border: 1px solid #e2e8f0; border-radius: 9px; padding: 11px 14px; gap: 12px; cursor: pointer; transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1); box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03);">
              <div class="sod-module-item-main" style="display: flex; align-items: center; gap: 10px; flex: 1; min-width: 0;">
                <span class="sod-module-item-icon" style="width: 28px; height: 28px; border-radius: 7px; background: #f8fafc; border: 1px solid #e2e8f0; color: #4f46e5; display: inline-flex; align-items: center; justify-content: center; flex-shrink: 0;">${this.workspaceIcon(
					item.label
				)}</span>
                <div class="sod-module-item-text" style="display: flex; align-items: center; gap: 8px; min-width: 0; flex-wrap: wrap;">
                  <span class="sod-module-item-name" style="font-size: 13.5px; font-weight: 600; color: #0f172a; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${frappe.utils.escape_html(
						item.label
					)}</span>
                  <span class="sod-module-item-kind-tag ${kindLower}" style="font-size: 9.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; padding: 2px 7px; border-radius: 4px; display: inline-block; line-height: 1.2; ${kStyle}">${frappe.utils.escape_html(
						kind
					)}</span>
                </div>
              </div>
            </div>
          `;
				});

				html += `
            </div>
          </div>
        `;
			});

			html += `
          </div>
        </div>
      `;
		}

		this.$content.html(html);
		this.bindPipelineClicks();

		// Render chart if present
		if (data.chart) {
			this.renderFrappeChart("#sod-generic-chart", {
				data: data.chart,
				type: "bar",
				colors: ["#5369ef", "#12b886"],
			});
		}
	}

	/* -------------------------------------------------------------
     PIPELINE MARKUP & MODAL (Comprehensive 24-Step Industrial Flow)
  ------------------------------------------------------------- */
	getMaster24Stages() {
		return [
			// Line 1: Commercial & Sales Engineering (Steps 1–8)
			{
				step_no: 1,
				id: "lead",
				label: "Lead / Inquiry",
				in_charge: "Sakshi Sawant / Narendra Sir",
				department: "Sales & Marketing",
				doctype: "Lead",
				icon: "💬",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 1,
			},
			{
				step_no: 2,
				id: "req_collection",
				label: "Requirement Collection",
				in_charge: "Narendra Sir / Raj / Samir Patil",
				department: "Technical Sales",
				doctype: "Opportunity",
				icon: "📋",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 1,
			},
			{
				step_no: 3,
				id: "tech_eval",
				label: "Technical Evaluation (Drawing)",
				in_charge: "Ubed / Tejas Patil",
				department: "Design & Engineering",
				doctype: "BOM",
				icon: "📐",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 1,
			},
			{
				step_no: 4,
				id: "costing",
				label: "Costing / Estimation",
				in_charge: "Estimation Team",
				department: "Costing & Finance",
				doctype: "Quotation",
				icon: "🧮",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 1,
			},
			{
				step_no: 5,
				id: "quotation",
				label: "Quotation",
				in_charge: "Sales Department",
				department: "Sales",
				doctype: "Quotation",
				icon: "📑",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 1,
			},
			{
				step_no: 6,
				id: "customer_po",
				label: "Customer PO & Approval",
				in_charge: "Akshay Patil",
				department: "Sales Administration",
				doctype: "Sales Order",
				icon: "🤝",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 1,
			},
			{
				step_no: 7,
				id: "po_verification",
				label: "PO Verification",
				in_charge: "Akshay Patil",
				department: "Sales Operations",
				doctype: "Sales Order",
				icon: "🔍",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 1,
			},
			{
				step_no: 8,
				id: "sales_order",
				label: "Create Sales Order",
				in_charge: "Akshay Patil",
				department: "Sales Operations",
				doctype: "Sales Order",
				icon: "📝",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 1,
			},

			// Line 2: Accounts, SCM, Planning & Fabrication (Steps 9–16)
			{
				step_no: 9,
				id: "accounts_approval",
				label: "Accounts Advance Approval",
				in_charge: "Pooja Chougule",
				department: "Accounts Team",
				doctype: "Payment Entry",
				icon: "💳",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 2,
			},
			{
				step_no: 10,
				id: "production_plan",
				label: "Production Planning",
				in_charge: "Swapnil Mohite",
				department: "PPC Department",
				doctype: "Production Plan",
				icon: "📊",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 2,
			},
			{
				step_no: 11,
				id: "bom",
				label: "Production Drawing (BOM)",
				in_charge: "Suraj Jirage",
				department: "Design & Engineering",
				doctype: "BOM",
				icon: "📄",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 2,
			},
			{
				step_no: 12,
				id: "store_avail",
				label: "Store Dept (Material Avail)",
				in_charge: "Abhishek Mohite",
				department: "Store Department",
				doctype: "Stock Entry",
				icon: "🏢",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 2,
			},
			{
				step_no: 13,
				id: "purchase_receipt",
				label: "Purchase & Material Receipt",
				in_charge: "Stores / Purchase Department",
				department: "Purchase",
				doctype: "Purchase Receipt",
				icon: "📦",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 2,
			},
			{
				step_no: 14,
				id: "raw_qc",
				label: "Raw Material QC",
				in_charge: "QC Department",
				department: "Quality Control",
				doctype: "Quality Inspection",
				icon: "🔬",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 2,
			},
			{
				step_no: 15,
				id: "laser_cutting",
				label: "Laser Cutting (Sheet & Pipe)",
				in_charge: "Laser Cutting Shop",
				department: "Fabrication",
				doctype: "Job Card",
				icon: "⚡",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 2,
			},
			{
				step_no: 16,
				id: "bending",
				label: "Bending (as per Drawing)",
				in_charge: "Bending Department",
				department: "Fabrication",
				doctype: "Job Card",
				icon: "📐",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 2,
			},

			// Line 3: Welding, Finishing, Quality & Dispatch (Steps 17–24)
			{
				step_no: 17,
				id: "cutting_qc",
				label: "Cutting & Bending QC",
				in_charge: "QC Department",
				department: "Quality Control",
				doctype: "Quality Inspection",
				icon: "🔍",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 3,
			},
			{
				step_no: 18,
				id: "welding",
				label: "Welding",
				in_charge: "Dhashrat Salavi",
				department: "Welding Shop",
				doctype: "Job Card",
				icon: "🔥",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 3,
			},
			{
				step_no: 19,
				id: "welding_qc",
				label: "Welding Quality Check",
				in_charge: "QC Department",
				department: "Quality Control",
				doctype: "Quality Inspection",
				icon: "🔎",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 3,
			},
			{
				step_no: 20,
				id: "grinding",
				label: "Grinding / Finishing",
				in_charge: "Dhashrat Salavi",
				department: "Finishing Shop",
				doctype: "Job Card",
				icon: "✨",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 3,
			},
			{
				step_no: 21,
				id: "painting",
				label: "Painting / Powder Coating",
				in_charge: "Babaso Aagale",
				department: "Coating Department",
				doctype: "Job Card",
				icon: "🎨",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 3,
			},
			{
				step_no: 22,
				id: "final_qc",
				label: "Final QC & Rework Assembly",
				in_charge: "QC / Shrikant Magdum",
				department: "Quality Assurance",
				doctype: "Quality Inspection",
				icon: "🎯",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 3,
			},
			{
				step_no: 23,
				id: "packing",
				label: "Packing & Transportation",
				in_charge: "Logistics Team",
				department: "Logistics",
				doctype: "Delivery Note",
				icon: "📦",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 3,
			},
			{
				step_no: 24,
				id: "documentation_dispatch",
				label: "Documentation & Dispatch",
				in_charge: "Pooja Chougule / Samir Patil",
				department: "Accounts, Dispatch & Field",
				doctype: "Sales Invoice / Delivery Note",
				icon: "🚚",
				defaultStatus: "wait",
				defaultBadge: "WAITING",
				lineNo: 3,
				note: "Encapsulates GST Tax Invoicing, Government E-Way Bill, Delivery Challan, Customer Gate Delivery, and Samir Patil Site Installation & Customer Feedback.",
			},
		];
	}

	resolvePipelineStages(p) {
		const master = this.getMaster24Stages();
		const serverStages = Array.isArray(p.stages) ? p.stages : [];
		const serverMapById = {};
		const serverMapByStep = {};

		serverStages.forEach((s) => {
			if (s.id) serverMapById[s.id] = s;
			if (s.step_no) serverMapByStep[s.step_no] = s;
		});

		// Also support legacy aliases if needed
		if (p.legacy_stages) {
			if (p.legacy_stages.work_order && !serverMapById["laser_cutting"]) {
				serverMapById["laser_cutting"] = p.legacy_stages.work_order;
			}
			if (p.legacy_stages.job_card && !serverMapById["welding"]) {
				serverMapById["welding"] = p.legacy_stages.job_card;
			}
			if (p.legacy_stages.stock_entry && !serverMapById["final_qc"]) {
				serverMapById["final_qc"] = p.legacy_stages.stock_entry;
			}
			if (p.legacy_stages.dispatch && !serverMapById["documentation_dispatch"]) {
				serverMapById["documentation_dispatch"] = p.legacy_stages.dispatch;
			}
		}

		return master.map((m) => {
			const live = serverMapById[m.id] || serverMapByStep[m.step_no] || {};
			const status = live.status || "wait";
			let badge = live.badge;
			if (!badge) {
				if (status === "done") badge = "✓ Completed";
				else if (status === "current") badge = "⚡ Active Now";
				else if (status === "fail") badge = "⚠ REWORK REQUIRED";
				else badge = "WAITING";
			}

			return {
				step_no: m.step_no,
				id: m.id,
				label: m.label,
				in_charge: m.in_charge,
				department: m.department,
				doctype: m.doctype,
				icon: m.icon,
				status: status,
				badge: badge,
				count: live.count !== undefined ? live.count : 0,
				records: live.records || [],
				info: live.info || m.note || "",
				lineNo: m.lineNo,
			};
		});
	}

	isManufacturingPipelineReady(p) {
		const stages = Array.isArray(p?.stages) ? p.stages : [];
		const verification =
			stages.find((stage) => Number(stage.step_no) === 7) ||
			stages.find((stage) => stage.id === "po_verification");
		return verification?.status === "done";
	}

	renderPipelineMarkup(p, visibleLines = [1, 2, 3]) {
		p = p || {};
		const stages = this.resolvePipelineStages(p);
		const visibleStages = stages.filter((stage) => visibleLines.includes(stage.lineNo));

		const currentStep =
			visibleStages.find((s) => s.status === "current") ||
			visibleStages.find((s) => s.status !== "done") ||
			visibleStages[visibleStages.length - 1];
		const completedCount = visibleStages.filter((s) => s.status === "done").length;
		const totalCount = visibleStages.length;
		const percent = Math.round((completedCount / totalCount) * 100);

		// Line configurations for 8 - 8 - 8 (24 cards) layout
		const lines = [
			{
				lineNo: 1,
				title: "LINE 1 · COMMERCIAL & SALES ENGINEERING (STEPS 1–8)",
				shortTitle: "Line 1: Commercial (1–8)",
				colorClass: "blue",
				stages: stages.slice(0, 8),
				handoverText: "Handover to Accounts, PPC & SCM Team (Pooja / Swapnil / Suraj / Abhishek)",
			},
			{
				lineNo: 2,
				title: "LINE 2 · ACCOUNTS, SCM, PLANNING & FABRICATION (STEPS 9–16)",
				shortTitle: "Line 2: Planning & SCM (9–16)",
				colorClass: "amber",
				stages: stages.slice(8, 16),
				handoverText:
					"Handover to Welding, Finishing, Quality & Dispatch (Dhashrat / Babaso / Samir)",
			},
			{
				lineNo: 3,
				title: "LINE 3 · WELDING, FINISHING, QUALITY & DISPATCH (STEPS 17–24)",
				shortTitle: "Line 3: Finishing & Handover (17–24)",
				colorClass: "purple",
				stages: stages.slice(16, 24),
				handoverText: "Complete Factory Pipeline Delivered, Installed & Signed Off",
			},
		].filter((line) => visibleLines.includes(line.lineNo));

		let html = `
      <div class="sod-pipeline-wrapper" data-pipeline-project="${frappe.utils.escape_html(p.project || "")}">
        <!-- Pipeline Control Bar -->
        <div class="sod-pipeline-header">
          <div class="sod-pipeline-tabs" data-target-project="${frappe.utils.escape_html(p.project || "")}">
            ${
				lines.length > 1
					? `<button class="sod-pipeline-tab active" data-line="all">All ${totalCount} Steps (${
							visibleStages[0].step_no
					  }–${visibleStages[totalCount - 1].step_no})</button>`
					: ""
			}
            ${lines
				.map(
					(line) =>
						`<button class="sod-pipeline-tab${lines.length === 1 ? " active" : ""}" data-line="${
							line.lineNo
						}">${line.shortTitle}</button>`
				)
				.join("")}
          </div>
          <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
            <div class="sod-pipeline-current-pill">
              <span class="sod-pulse-dot"></span>
              <span>⚡ Live Step: <b>${frappe.utils.escape_html(
					currentStep.label || ""
				)}</b> · <i>${frappe.utils.escape_html(currentStep.in_charge || "Operations")}</i></span>
            </div>
            <div class="sod-pipeline-progress-badge">
              <span style="font-size:12px; font-weight:800; color:#1e293b;">
                ${completedCount}/${totalCount} Done (${percent}%)
              </span>
              <div class="sod-mini-progress-bar">
                <div class="sod-mini-progress-fill" style="width: ${percent}%;"></div>
              </div>
            </div>
          </div>
        </div>

        <!-- 3-Line Matrix Track -->
        <div class="sod-pipeline-flow-matrix" id="sod-pipe-track-${frappe.utils.escape_html(
			p.project || ""
		)}">
    `;

		lines.forEach((ln, lineIdx) => {
			html += `
        <div class="sod-pipeline-line-section" data-line-section="${ln.lineNo}">
          <!-- Line Header Banner -->
          <div class="sod-line-header-badge line-${ln.colorClass}">
            <div class="sod-line-header-left">
              <span class="sod-line-dot"></span>
              <span class="sod-line-title">${ln.title}</span>
            </div>
            <div class="sod-line-header-right">
              <span class="sod-line-count-tag">${ln.stages.length} Steps Connected</span>
            </div>
          </div>

          <!-- Cards Row (Compact 8 cards per line) -->
          <div class="sod-line-cards-row-wrap">
            <div class="sod-line-cards-row">
      `;

			ln.stages.forEach((st, idxInLine) => {
				const stepNum = st.step_no;
				const stepNumStr = stepNum < 10 ? "0" + stepNum : "" + stepNum;

				const statusIcon =
					st.status === "done"
						? "✓"
						: st.status === "current"
						? "⚡"
						: st.status === "fail"
						? "⚠"
						: st.icon || "○";

				const statusLabel =
					st.status === "done"
						? "DONE"
						: st.status === "current"
						? "ACTIVE"
						: st.status === "fail"
						? "REWORK"
						: "WAITING";

				html += `
          <div class="sod-card-step ${st.status} line-${ln.lineNo}" role="button" tabindex="0"
            data-project="${frappe.utils.escape_html(p.project || "")}"
            data-stage-id="${frappe.utils.escape_html(st.id)}"
            data-step-no="${stepNum}"
            data-line-no="${ln.lineNo}"
            title="Step ${stepNumStr}: ${frappe.utils.escape_html(
					st.label
				)} (${statusLabel}) — Click to inspect live ERPNext records">

            <div class="sod-card-step-top">
              <span class="sod-card-step-num">#${stepNumStr}</span>
              <span class="sod-card-status-pill ${st.status}">${statusLabel}</span>
            </div>

            <div class="sod-card-step-icon-wrap">
              <div class="sod-card-step-circle ${st.status}">
                ${statusIcon}
              </div>
            </div>

            <strong class="sod-card-step-name">${frappe.utils.escape_html(st.label)}</strong>

            <div class="sod-card-step-incharge" title="In-Charge: ${frappe.utils.escape_html(
				st.in_charge || ""
			)}">
              <span class="sod-incharge-badge">👤 ${frappe.utils.escape_html(
					st.in_charge || "Operations"
				)}</span>
            </div>

            <div class="sod-card-step-badge ${st.status}">
              ${frappe.utils.escape_html(st.badge || statusLabel)}
            </div>
          </div>
        `;

				// Intermediate connector between adjacent cards in this line (7 connectors per line)
				if (idxInLine < ln.stages.length - 1) {
					const nextSt = ln.stages[idxInLine + 1];
					let connClass = "wait";
					if (st.status === "done" && nextSt.status === "done") {
						connClass = "done";
					} else if (st.status === "done" && nextSt.status === "current") {
						connClass = "active";
					} else if (st.status === "current") {
						connClass = "pulse";
					}
					html += `
            <div class="sod-row-connector ${connClass}">
              <div class="sod-conn-line"></div>
              <div class="sod-conn-arrow">›</div>
            </div>
          `;
				}
			});

			html += `
            </div>
          </div>
        </div>
      `;

			// Inter-line Turn Bridge between Line 1 -> Line 2, and Line 2 -> Line 3
			if (lineIdx < lines.length - 1) {
				const lastStOfLine = ln.stages[ln.stages.length - 1];
				const nextLine = lines[lineIdx + 1];
				const firstStOfNextLine = nextLine.stages[0];

				const isBridgeDone =
					lastStOfLine &&
					lastStOfLine.status === "done" &&
					firstStOfNextLine &&
					(firstStOfNextLine.status === "done" || firstStOfNextLine.status === "current");
				const bridgeClass = isBridgeDone
					? firstStOfNextLine.status === "current"
						? "active"
						: "done"
					: "wait";

				html += `
          <div class="sod-pipeline-turn-container ${bridgeClass}" data-turn-from="${
					ln.lineNo
				}" data-turn-to="${nextLine.lineNo}">
            <div class="sod-turn-drop-connector-right" title="Connecting Line ${ln.lineNo} (Card #${
					ln.lineNo * 8
				}) to Handover Bridge"></div>
            <div class="sod-turn-track">
              <div class="sod-turn-wire-left">
                <span class="sod-turn-wire-dir left">◀</span>
              </div>
              <div class="sod-turn-label-pill">
                <span class="sod-turn-icon">↳</span>
                <span class="sod-turn-text">${ln.handoverText}</span>
                <span class="sod-turn-arrow">▼</span>
              </div>
              <div class="sod-turn-wire-right">
                <span class="sod-turn-wire-dir right">▼</span>
              </div>
            </div>
            <div class="sod-turn-drop-connector-left" title="Connecting Handover Bridge to Line ${
				nextLine.lineNo
			} (Card #${ln.lineNo * 8 + 1})"></div>
          </div>
        `;
			}
		});

		html += `
        </div>
      </div>
    `;
		return html;
	}

	getAvatarGradient(name) {
		const gradients = [
			"linear-gradient(135deg, #3b82f6, #1d4ed8)",
			"linear-gradient(135deg, #06b6d4, #0891b2)",
			"linear-gradient(135deg, #10b981, #059669)",
			"linear-gradient(135deg, #f59e0b, #d97706)",
			"linear-gradient(135deg, #ec4899, #be185d)",
			"linear-gradient(135deg, #8b5cf6, #6d28d9)",
			"linear-gradient(135deg, #f97316, #c2410c)",
			"linear-gradient(135deg, #14b8a6, #0f766e)",
		];
		let hash = 0;
		for (let i = 0; i < (name || "").length; i++) {
			hash = name.charCodeAt(i) + ((hash << 5) - hash);
		}
		return gradients[Math.abs(hash) % gradients.length];
	}

	renderStrategicPipelineSheet(pipelines) {
		if (!pipelines || !pipelines.length) {
			return '<div class="sod-empty">No active in-progress manufacturing projects found matching filters.</div>';
		}

		const steps = [
			{
				step_no: 1,
				numStr: "#01",
				title: "Lead / Inquiry",
				cleanTitle: "Lead / Inquiry",
				id: "lead",
				colorTheme: "col-cyan",
			},
			{
				step_no: 2,
				numStr: "#02",
				title: "Requirement Collection",
				cleanTitle: "Requirement Collection",
				id: "req_collection",
				colorTheme: "col-blue",
			},
			{
				step_no: 3,
				numStr: "#03",
				title: "WAITING Technical Evaluation (Drawing)",
				cleanTitle: "Technical Evaluation (Drawing)",
				waitPrefix: true,
				id: "tech_eval",
				colorTheme: "col-amber",
			},
			{
				step_no: 4,
				numStr: "#04",
				title: "WAITING Costing / Estimation",
				cleanTitle: "Costing / Estimation",
				waitPrefix: true,
				id: "costing",
				colorTheme: "col-violet",
			},
			{
				step_no: 5,
				numStr: "#05",
				title: "Quotation",
				cleanTitle: "Quotation",
				id: "quotation",
				colorTheme: "col-indigo",
			},
			{
				step_no: 6,
				numStr: "#06",
				title: "Customer PO & Approval",
				cleanTitle: "Customer PO & Approval",
				id: "customer_po",
				colorTheme: "col-emerald",
			},
			{
				step_no: 7,
				numStr: "#07",
				title: "PO Verification",
				cleanTitle: "PO Verification",
				id: "po_verification",
				colorTheme: "col-teal",
			},
			{
				step_no: 8,
				numStr: "#08",
				title: "Create Sales Order",
				cleanTitle: "Create Sales Order",
				id: "sales_order",
				colorTheme: "col-green",
			},
		];

		let html = `
      <div class="sod-matrix-wrapper">
        <div class="sod-matrix-toolbar">
          <div class="sod-matrix-search-wrap">
            <span class="sod-matrix-search-icon">🔍</span>
            <input type="search" class="sod-matrix-search" id="sod-matrix-pipeline-search" placeholder="Search customer name or project ID in matrix…" />
          </div>
          <div class="sod-matrix-legend">
            <span class="sod-matrix-legend-item"><span class="sod-matrix-icon-legend done">✔</span> <b>Done</b></span>
            <span class="sod-matrix-legend-item"><span class="sod-matrix-icon-legend waiting">⏳</span> <b>Waiting</b></span>
            <span class="sod-matrix-legend-item"><span class="sod-matrix-icon-legend not-done">✖</span> <b>Not Done</b></span>
          </div>
        </div>

        <div class="sod-matrix-scroll-container">
          <table class="sod-matrix-table" id="sod-strategic-pipeline-matrix">
            <thead>
              <tr>
                <th class="sod-matrix-th sod-matrix-col-customer">
                  <div class="sod-matrix-th-stripe" style="background: linear-gradient(90deg, #1e293b, #475569);"></div>
                  <div class="sod-matrix-th-inner">
                    <span class="sod-matrix-th-num" style="background:#e2e8f0; color:#1e293b;">#</span>
                    <span class="sod-matrix-th-title">Customer Name</span>
                    <span class="sod-matrix-th-sub">Active Projects</span>
                  </div>
                </th>
                ${steps
					.map(
						(st) => `
                  <th class="sod-matrix-th sod-matrix-col-step ${st.colorTheme}" data-step-no="${st.step_no}">
                    <div class="sod-matrix-th-stripe"></div>
                    <div class="sod-matrix-th-inner">
                      <span class="sod-matrix-th-num ${st.colorTheme}">${st.numStr}</span>
                      ${st.waitPrefix ? `<span class="sod-matrix-wait-badge">WAITING</span>` : ""}
                      <span class="sod-matrix-th-title">${frappe.utils.escape_html(
							st.cleanTitle || st.title
						)}</span>
                    </div>
                  </th>
                `
					)
					.join("")}
                <th class="sod-matrix-th sod-matrix-col-status">
                  <div class="sod-matrix-th-stripe" style="background: linear-gradient(90deg, #3b82f6, #6366f1);"></div>
                  <div class="sod-matrix-th-inner">
                    <span class="sod-matrix-th-num" style="background:#dbeafe; color:#1d4ed8;">LINE 1</span>
                    <span class="sod-matrix-th-title">Overall Status</span>
                    <span class="sod-matrix-th-sub">Commercial Velocity</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
    `;

		pipelines.forEach((p, idx) => {
			const allStages = this.resolvePipelineStages(p);
			const line1Stages = allStages.slice(0, 8);
			const doneCount = line1Stages.filter((s) => s.status === "done").length;
			const pct = Math.round((doneCount / 8) * 100);
			const custLetter = (p.customer || "P").trim()[0].toUpperCase();
			const avatarBg = this.getAvatarGradient(p.customer);

			html += `
        <tr class="sod-matrix-row" data-project="${frappe.utils.escape_html(
			p.project
		)}" data-customer="${frappe.utils.escape_html(p.customer || "")}">
          <!-- Sticky 1st Column: Customer Name & Project ID -->
          <td class="sod-matrix-td sod-matrix-cell-customer">
            <div class="sod-matrix-customer-wrap">
              <span class="sod-matrix-avatar" style="background:${avatarBg};">${custLetter}</span>
              <div class="sod-matrix-customer-info">
                <strong class="sod-matrix-customer-title" title="${frappe.utils.escape_html(
					p.customer || "Customer Unassigned"
				)}">
                  <a href="/app/customer/${encodeURIComponent(
						p.customer || ""
					)}" target="_blank" class="sod-matrix-cust-link" onclick="event.stopPropagation()">
                    ${frappe.utils.escape_html(p.customer || "Customer Unassigned")}
                  </a>
                </strong>
                <div class="sod-matrix-project-meta">
                  <a href="/app/project/${encodeURIComponent(
						p.project
					)}" target="_blank" class="sod-matrix-proj-code" onclick="event.stopPropagation()">${frappe.utils.escape_html(
				p.project
			)}</a>
                  <span class="sod-matrix-proj-title" title="${frappe.utils.escape_html(
						p.project_name
					)}">${frappe.utils.escape_html(p.project_name)}</span>
                </div>
              </div>
            </div>
          </td>
      `;

			// 8 Step Columns
			steps.forEach((stepMeta, stepIdx) => {
				const st = line1Stages[stepIdx] || {};
				const isDone = st.status === "done";
				const isWaiting = st.status === "current" || st.status === "active";
				const isFail = st.status === "fail";

				let statusKey = "not-done";
				let statusBadge = "Not Done";
				let statusIcon = "✖";

				if (isDone) {
					statusKey = "done";
					statusBadge = "Done";
					statusIcon = "✔";
				} else if (isWaiting || isFail) {
					statusKey = "waiting";
					statusBadge = "Waiting";
					statusIcon = "⏳";
				}

				const subtitle = isDone
					? st.info || "Verified"
					: isWaiting
					? st.in_charge
						? `👤 ${st.in_charge}`
						: "In Progress"
					: "Pending";

				html += `
          <td class="sod-matrix-td sod-matrix-step-cell ${statusKey}"
              data-project="${frappe.utils.escape_html(p.project)}"
              data-stage-id="${frappe.utils.escape_html(st.id || stepMeta.id)}"
              data-step-no="${stepMeta.step_no}"
              title="Step ${stepMeta.numStr}: ${frappe.utils.escape_html(
					stepMeta.title
				)} — ${statusBadge}. Click to inspect live records.">
            <div class="sod-matrix-cell-content">
              <span class="sod-matrix-icon ${statusKey}">${statusIcon}</span>
              <span class="sod-matrix-subtext ${statusKey}" title="${frappe.utils.escape_html(
					subtitle
				)}">${frappe.utils.escape_html(subtitle)}</span>
            </div>
          </td>
        `;
			});

			// Overall Progress Column
			html += `
          <td class="sod-matrix-td sod-matrix-cell-progress">
            <div class="sod-matrix-prog-box">
              <span class="sod-matrix-prog-pill ${
					pct === 100 ? "done" : pct > 0 ? "active" : "wait"
				}">${doneCount}/8 Done (${pct}%)</span>
              <div class="sod-matrix-prog-bar">
                <div class="sod-matrix-prog-fill ${pct === 100 ? "done" : ""}" style="width: ${pct}%;"></div>
              </div>
            </div>
          </td>
        </tr>
      `;
		});

		html += `
            </tbody>
          </table>
        </div>
      </div>
    `;

		return html;
	}

	renderManufacturingDeliverySheet(pipelines) {
		if (!pipelines || !pipelines.length) {
			return '<div class="sod-empty">No active manufacturing projects found matching filters.</div>';
		}

		const steps = [
			// Line 2: Accounts, SCM, Planning & Fabrication (Steps 9–16)
			{
				step_no: 9,
				numStr: "#09",
				lineNo: 2,
				lineName: "Line 2",
				title: "Accounts Advance Approval",
				id: "accounts_approval",
				colorTheme: "col-amber",
			},
			{
				step_no: 10,
				numStr: "#10",
				lineNo: 2,
				lineName: "Line 2",
				title: "Production Planning",
				id: "production_plan",
				colorTheme: "col-blue",
			},
			{
				step_no: 11,
				numStr: "#11",
				lineNo: 2,
				lineName: "Line 2",
				title: "Production Drawing (BOM)",
				id: "bom",
				colorTheme: "col-indigo",
			},
			{
				step_no: 12,
				numStr: "#12",
				lineNo: 2,
				lineName: "Line 2",
				title: "Store Dept (Material Avail)",
				id: "store_avail",
				colorTheme: "col-teal",
			},
			{
				step_no: 13,
				numStr: "#13",
				lineNo: 2,
				lineName: "Line 2",
				title: "Purchase & Material Receipt",
				id: "purchase_receipt",
				colorTheme: "col-violet",
			},
			{
				step_no: 14,
				numStr: "#14",
				lineNo: 2,
				lineName: "Line 2",
				title: "Raw Material QC",
				id: "raw_qc",
				colorTheme: "col-fuchsia",
			},
			{
				step_no: 15,
				numStr: "#15",
				lineNo: 2,
				lineName: "Line 2",
				title: "Laser Cutting (Sheet & Pipe)",
				id: "laser_cutting",
				colorTheme: "col-orange",
			},
			{
				step_no: 16,
				numStr: "#16",
				lineNo: 2,
				lineName: "Line 2",
				title: "Bending (as per Drawing)",
				id: "bending",
				colorTheme: "col-rose",
			},

			// Line 3: Welding, Finishing, Quality & Dispatch (Steps 17–24)
			{
				step_no: 17,
				numStr: "#17",
				lineNo: 3,
				lineName: "Line 3",
				title: "Cutting & Bending QC",
				id: "cutting_qc",
				colorTheme: "col-emerald",
			},
			{
				step_no: 18,
				numStr: "#18",
				lineNo: 3,
				lineName: "Line 3",
				title: "Welding",
				id: "welding",
				colorTheme: "col-red",
			},
			{
				step_no: 19,
				numStr: "#19",
				lineNo: 3,
				lineName: "Line 3",
				title: "Welding Quality Check",
				id: "welding_qc",
				colorTheme: "col-pink",
			},
			{
				step_no: 20,
				numStr: "#20",
				lineNo: 3,
				lineName: "Line 3",
				title: "Grinding / Finishing",
				id: "grinding",
				colorTheme: "col-purple",
			},
			{
				step_no: 21,
				numStr: "#21",
				lineNo: 3,
				lineName: "Line 3",
				title: "Painting / Powder Coating",
				id: "painting",
				colorTheme: "col-cyan",
			},
			{
				step_no: 22,
				numStr: "#22",
				lineNo: 3,
				lineName: "Line 3",
				title: "Final QC & Rework Assembly",
				id: "final_qc",
				colorTheme: "col-blue",
			},
			{
				step_no: 23,
				numStr: "#23",
				lineNo: 3,
				lineName: "Line 3",
				title: "Packing & Transportation",
				id: "packing",
				colorTheme: "col-amber",
			},
			{
				step_no: 24,
				numStr: "#24",
				lineNo: 3,
				lineName: "Line 3",
				title: "Documentation & Dispatch",
				id: "documentation_dispatch",
				colorTheme: "col-green",
			},
		];

		let html = `
      <div class="sod-matrix-wrapper sod-mfg-matrix-wrapper">
        <div class="sod-matrix-toolbar">
          <div class="sod-matrix-search-wrap">
            <span class="sod-matrix-search-icon">🔍</span>
            <input type="search" class="sod-matrix-search" id="sod-matrix-mfg-search" placeholder="Filter manufacturing projects or clients in sheet…" />
          </div>
          <div class="sod-matrix-filter-tabs">
            <button class="sod-matrix-filter-tab active" data-filter-line="all">All Steps #09–#24 (16 Steps)</button>
            <button class="sod-matrix-filter-tab" data-filter-line="2">Line 2: Planning &amp; SCM (#09–#16)</button>
            <button class="sod-matrix-filter-tab" data-filter-line="3">Line 3: Finishing &amp; Dispatch (#17–#24)</button>
          </div>
          <div class="sod-matrix-legend">
            <span class="sod-matrix-legend-item"><span class="sod-matrix-icon-legend done">✔</span> <b>Done</b></span>
            <span class="sod-matrix-legend-item"><span class="sod-matrix-icon-legend waiting">⏳</span> <b>Waiting</b></span>
            <span class="sod-matrix-legend-item"><span class="sod-matrix-icon-legend not-done">✖</span> <b>Not Done</b></span>
          </div>
        </div>

        <div class="sod-matrix-scroll-container">
          <table class="sod-matrix-table" id="sod-mfg-pipeline-matrix">
            <thead>
              <tr>
                <th class="sod-matrix-th sod-matrix-col-customer">
                  <div class="sod-matrix-th-stripe" style="background: linear-gradient(90deg, #1e293b, #475569);"></div>
                  <div class="sod-matrix-th-inner">
                    <span class="sod-matrix-th-num" style="background:#e2e8f0; color:#1e293b;">#</span>
                    <span class="sod-matrix-th-title">Customer Name</span>
                    <span class="sod-matrix-th-sub">Active Production</span>
                  </div>
                </th>
                ${steps
					.map(
						(st) => `
                  <th class="sod-matrix-th sod-matrix-col-step ${st.colorTheme}" data-step-no="${
							st.step_no
						}" data-line-no="${st.lineNo}">
                    <div class="sod-matrix-th-stripe"></div>
                    <div class="sod-matrix-th-inner">
                      <span class="sod-matrix-th-num ${st.colorTheme}">${st.numStr}</span>
                      <span class="sod-matrix-line-pill ${st.lineNo === 2 ? "line2" : "line3"}">${
							st.lineName
						}</span>
                      <span class="sod-matrix-th-title">${frappe.utils.escape_html(st.title)}</span>
                    </div>
                  </th>
                `
					)
					.join("")}
                <th class="sod-matrix-th sod-matrix-col-status">
                  <div class="sod-matrix-th-stripe" style="background: linear-gradient(90deg, #10b981, #059669);"></div>
                  <div class="sod-matrix-th-inner">
                    <span class="sod-matrix-th-num" style="background:#dcfce7; color:#15803d;">LINE 2 &amp; 3</span>
                    <span class="sod-matrix-th-title">Mfg Yield</span>
                    <span class="sod-matrix-th-sub">Shopfloor Velocity</span>
                  </div>
                </th>
              </tr>
            </thead>
            <tbody>
    `;

		pipelines.forEach((p, idx) => {
			const allStages = this.resolvePipelineStages(p);
			const mfgStages = allStages.slice(8, 24); // Steps 9-24 (index 8 to 23)
			const doneCount = mfgStages.filter((s) => s.status === "done").length;
			const pct = Math.round((doneCount / 16) * 100);
			const custLetter = (p.customer || "P").trim()[0].toUpperCase();
			const avatarBg = this.getAvatarGradient(p.customer);

			html += `
        <tr class="sod-matrix-row" data-project="${frappe.utils.escape_html(
			p.project
		)}" data-customer="${frappe.utils.escape_html(p.customer || "")}">
          <!-- Sticky 1st Column: Customer Name & Project ID -->
          <td class="sod-matrix-td sod-matrix-cell-customer">
            <div class="sod-matrix-customer-wrap">
              <span class="sod-matrix-avatar" style="background:${avatarBg};">${custLetter}</span>
              <div class="sod-matrix-customer-info">
                <strong class="sod-matrix-customer-title" title="${frappe.utils.escape_html(
					p.customer || "Customer Unassigned"
				)}">
                  <a href="/app/customer/${encodeURIComponent(
						p.customer || ""
					)}" target="_blank" class="sod-matrix-cust-link" onclick="event.stopPropagation()">
                    ${frappe.utils.escape_html(p.customer || "Customer Unassigned")}
                  </a>
                </strong>
                <div class="sod-matrix-project-meta">
                  <a href="/app/project/${encodeURIComponent(
						p.project
					)}" target="_blank" class="sod-matrix-proj-code" onclick="event.stopPropagation()">${frappe.utils.escape_html(
				p.project
			)}</a>
                  <span class="sod-matrix-proj-title" title="${frappe.utils.escape_html(
						p.project_name
					)}">${frappe.utils.escape_html(p.project_name)}</span>
                </div>
              </div>
            </div>
          </td>
      `;

			// 16 Step Columns (Steps 9–24)
			steps.forEach((stepMeta, stepIdx) => {
				const st = mfgStages[stepIdx] || {};
				const isDone = st.status === "done";
				const isWaiting = st.status === "current" || st.status === "active";
				const isFail = st.status === "fail";

				let statusKey = "not-done";
				let statusBadge = "Not Done";
				let statusIcon = "✖";

				if (isDone) {
					statusKey = "done";
					statusBadge = "Done";
					statusIcon = "✔";
				} else if (isWaiting || isFail) {
					statusKey = "waiting";
					statusBadge = "Waiting";
					statusIcon = "⏳";
				}

				const subtitle = isDone
					? st.badge || st.info || "Verified"
					: isWaiting
					? st.in_charge
						? `👤 ${st.in_charge}`
						: "Active Now"
					: "Pending Prior Step";

				html += `
          <td class="sod-matrix-td sod-matrix-step-cell ${statusKey}"
              data-project="${frappe.utils.escape_html(p.project)}"
              data-stage-id="${frappe.utils.escape_html(st.id || stepMeta.id)}"
              data-step-no="${stepMeta.step_no}"
              data-line-no="${stepMeta.lineNo}"
              title="Step ${stepMeta.numStr}: ${frappe.utils.escape_html(
					stepMeta.title
				)} — ${statusBadge}. Click to inspect live records.">
            <div class="sod-matrix-cell-content">
              <span class="sod-matrix-icon ${statusKey}">${statusIcon}</span>
              <span class="sod-matrix-subtext ${statusKey}" title="${frappe.utils.escape_html(
					subtitle
				)}">${frappe.utils.escape_html(subtitle)}</span>
            </div>
          </td>
        `;
			});

			// Overall Progress Column (Line 2 & 3)
			html += `
          <td class="sod-matrix-td sod-matrix-cell-progress">
            <div class="sod-matrix-prog-box">
              <span class="sod-matrix-prog-pill ${
					pct === 100 ? "done" : pct > 0 ? "active" : "wait"
				}">${doneCount}/16 Done (${pct}%)</span>
              <div class="sod-matrix-prog-bar">
                <div class="sod-matrix-prog-fill ${pct === 100 ? "done" : ""}" style="width: ${pct}%;"></div>
              </div>
            </div>
          </td>
        </tr>
      `;
		});

		html += `
            </tbody>
          </table>
        </div>
      </div>
    `;

		return html;
	}

	bindPipelineClicks() {
		const self = this;
		// Bind card/cell click to inspect linked records modal (support .sod-stage, .sod-card-step, .sod-matrix-step-cell, .sod-sheet-step-cell)
		this.$content.off("click", ".sod-stage, .sod-card-step, .sod-matrix-step-cell, .sod-sheet-step-cell");
		this.$content.on(
			"click",
			".sod-stage, .sod-card-step, .sod-matrix-step-cell, .sod-sheet-step-cell",
			function () {
				const project = $(this).data("project");
				const stageId = $(this).data("stage-id");
				if (project && stageId) {
					self.showStageModal(project, stageId);
				}
			}
		);

		// Real-time matrix search filter for Strategic Pipeline table
		this.$content.off("input", "#sod-matrix-pipeline-search, #sod-sheet-pipeline-search");
		this.$content.on("input", "#sod-matrix-pipeline-search, #sod-sheet-pipeline-search", function () {
			const q = $(this).val().toLowerCase().trim();
			self.$content
				.find("#sod-strategic-pipeline-matrix tbody tr, #sod-strategic-pipeline-sheet tbody tr")
				.each(function () {
					const text = $(this).text().toLowerCase();
					$(this).toggle(!q || text.indexOf(q) > -1);
				});
		});

		// Real-time matrix search filter for Manufacturing & Delivery table
		this.$content.off("input", "#sod-matrix-mfg-search");
		this.$content.on("input", "#sod-matrix-mfg-search", function () {
			const q = $(this).val().toLowerCase().trim();
			self.$content.find("#sod-mfg-pipeline-matrix tbody tr").each(function () {
				const text = $(this).text().toLowerCase();
				$(this).toggle(!q || text.indexOf(q) > -1);
			});
		});

		// Filter tabs for Manufacturing matrix (All / Line 2 / Line 3)
		this.$content.off("click", ".sod-matrix-filter-tab");
		this.$content.on("click", ".sod-matrix-filter-tab", function () {
			const $btn = $(this);
			const line = $btn.data("filter-line");
			$btn.siblings().removeClass("active");
			$btn.addClass("active");

			const $table = self.$content.find("#sod-mfg-pipeline-matrix");
			if (line === "all") {
				$table.find("[data-line-no]").show();
			} else {
				$table.find("[data-line-no]").each(function () {
					const l = String($(this).data("line-no"));
					if (l === String(line)) {
						$(this).show();
					} else {
						$(this).hide();
					}
				});
			}
		});

		// Line / Phase tabs filtering
		this.$content.off("click", ".sod-pipeline-tab");
		this.$content.on("click", ".sod-pipeline-tab", function () {
			const $btn = $(this);
			const lineChoice = String($btn.data("line") || "all");
			const targetProject = $btn.closest(".sod-pipeline-tabs").data("target-project");
			$btn.siblings().removeClass("active");
			$btn.addClass("active");

			const $track = self.$content.find(`#sod-pipe-track-${targetProject}`);
			if (lineChoice === "all") {
				$track.find(".sod-pipeline-line-section").show();
				$track.find(".sod-pipeline-turn-container").show();
			} else {
				$track.find(".sod-pipeline-line-section").each(function () {
					const lNo = String($(this).data("line-section"));
					if (lNo === lineChoice) {
						$(this).show();
					} else {
						$(this).hide();
					}
				});
				$track.find(".sod-pipeline-turn-container").hide();
			}
		});
	}

	showQuickDetails(action) {
		if (this.moduleBrowser?.openAction(action)) return;
		const esc = (value) => frappe.utils.escape_html(String(value ?? "—"));
		const dialog = new frappe.ui.Dialog({
			title: action.label.replace(/\s*\(\+ New\)/i, "").replace(/^New /, ""),
			size: "extra-large",
			fields: [{ fieldtype: "HTML", fieldname: "details" }],
		});
		const host = dialog.fields_dict.details.$wrapper;
		let offset = 0,
			search = "",
			sequence = 0,
			timer,
			activeName = null,
			busy = false,
			lastInput = 0;
		host.on("input", () => {
			lastInput = Date.now();
		});
		const filters = this.getFilters();
		const format = (value, type) => {
			if (value === null || value === undefined || value === "") return "—";
			if (["Currency", "Float", "Int", "Percent"].includes(type) && Number.isFinite(Number(value))) {
				return (
					new Intl.NumberFormat("en-IN", { maximumFractionDigits: type === "Int" ? 0 : 2 }).format(
						Number(value)
					) + (type === "Percent" ? "%" : "")
				);
			}
			return value;
		};
		const load = async (name = null, restoreSearch = false, background = false) => {
			activeName = name;
			busy = true;
			const request = ++sequence;
			if (!background)
				host.html('<div class="sod-quick-loading" role="status">Loading live details…</div>');
			try {
				const response = await frappe.call({
					method: "sarathi_owner.api.quick_details.get_details",
					args: {
						route: action.route,
						filters: JSON.stringify(filters),
						search,
						start: offset,
						name,
					},
				});
				if (request !== sequence) return;
				const data = response.message || {};
				const toolbar = `<div class="sod-quick-toolbar"><span class="sod-quick-tag">${esc(
					data.doctype || "LIVE REPORT"
				)}</span><span>Read-only details · Updated ${esc(
					new Date().toLocaleTimeString()
				)} · Read-only</span></div>`;
				if (data.error || data.restricted) {
					host.html(
						toolbar +
							`<div class="sod-quick-empty" role="alert">${esc(
								data.message || data.error
							)}</div>`
					);
					return;
				}
				if (data.kind === "record") {
					host.html(
						toolbar +
							`${
								name
									? '<button class="sod-quick-back" type="button">← Back to records</button>'
									: ""
							}<h3>${esc(data.name)}</h3><div class="sod-quick-fields">${
								(data.fields || [])
									.map(
										(f) =>
											`<div><small>${esc(f.label)}</small><strong>${esc(
												f.fieldtype === "Check"
													? f.value
														? "Yes"
														: "No"
													: format(f.value, f.fieldtype)
											)}</strong></div>`
									)
									.join("") || "<p>No saved details are available.</p>"
							}</div>`
					);
					host.find(".sod-quick-back").on("click", () => load());
					return;
				}
				const columns = (data.columns || []).map((col, i) =>
					typeof col === "string" ? { label: col.split(":")[0], fieldname: i } : col
				);
				const rows = (data.result || []).map((row) => row || {});
				const shareholderSelect = data.shareholders?.length
					? `<label class="sod-quick-search">Shareholder<select data-shareholder>${data.shareholders
							.map(
								(item) =>
									`<option value="${esc(item.name)}" ${
										data.filters?.shareholder === item.name ? "selected" : ""
									}>${esc(item.title || item.name)}</option>`
							)
							.join("")}</select></label>`
					: "";
				host.html(
					toolbar +
						shareholderSelect +
						`<label class="sod-quick-search">Search ${
							data.kind === "report" ? "report results" : "records"
						}<input type="search" value="${esc(
							search
						)}" placeholder="Search by name or ID…"></label><div class="sod-quick-table"><table><thead><tr>${columns
							.map((c) => `<th>${esc(c.label)}</th>`)
							.join("")}</tr></thead><tbody>${rows
							.map(
								(row, i) =>
									`<tr>${columns
										.map(
											(col, j) =>
												`<td>${
													data.kind === "list" && j === 0
														? `<button type="button" data-record="${i}">${esc(
																row.name
														  )}</button>`
														: esc(
																format(
																	Array.isArray(row)
																		? row[j]
																		: row[col.fieldname],
																	col.fieldtype
																)
														  )
												}</td>`
										)
										.join("")}</tr>`
							)
							.join("")}</tbody></table></div><p class="sod-quick-empty" ${
							rows.length ? "hidden" : ""
						}>No matching records for the selected filters.</p><div class="sod-quick-footer"><span>${
							data.kind === "report"
								? rows.length + " report rows"
								: rows.length
								? `${offset + 1}–${offset + rows.length} records`
								: "0 records"
						}</span>${
							data.kind === "list"
								? `<button type="button" data-previous ${
										offset ? "" : "disabled"
								  }>← Previous</button><button type="button" data-next ${
										data.has_more ? "" : "disabled"
								  }>Next →</button>`
								: ""
						}</div>`
				);
				host.find("[data-shareholder]").on("change", (event) => {
					filters.shareholder = event.target.value;
					load();
				});
				host.find("[data-record]").on("click", (event) =>
					load(rows[Number(event.currentTarget.dataset.record)].name)
				);
				host.find("[data-previous]").on("click", () => {
					offset = Math.max(0, offset - 25);
					load();
				});
				host.find("[data-next]").on("click", () => {
					offset += 25;
					load();
				});
				host.find('input[type="search"]').on("input", (event) => {
					search = event.target.value;
					if (data.kind === "report") {
						host.find("tbody tr").each(function () {
							$(this).toggle($(this).text().toLowerCase().includes(search.toLowerCase()));
						});
					} else {
						clearTimeout(timer);
						timer = setTimeout(() => {
							offset = 0;
							load(null, true);
						}, 400);
					}
				});
				if (data.kind === "report" && search)
					host.find("tbody tr").each(function () {
						$(this).toggle($(this).text().toLowerCase().includes(search.toLowerCase()));
					});
				if (restoreSearch) host.find('input[type="search"]').trigger("focus");
			} catch (error) {
				if (request === sequence)
					host.html(
						'<div class="sod-quick-empty" role="alert">These details could not be loaded. Check your access or try again.</div><button type="button" class="sod-quick-retry">Retry</button>'
					);
				host.find(".sod-quick-retry").on("click", () => load(name));
			} finally {
				if (request === sequence) busy = false;
			}
		};
		const refreshDetails = () => {
			if (!busy && !document.hidden && Date.now() - lastInput > 1500)
				load(activeName, host.find('input[type="search"]').is(":focus"), true);
		};
		const detailTimer = setInterval(refreshDetails, 15000);
		frappe.realtime?.on("sarathi_owner_live_change", refreshDetails);
		dialog.onhide = () => {
			sequence++;
			clearTimeout(timer);
			clearInterval(detailTimer);
			frappe.realtime?.off("sarathi_owner_live_change", refreshDetails);
			dialog.$wrapper.remove();
		};
		dialog.show();
		load();
	}

	showCardDetailModal(label, value, desc, action, route) {
		this.$modalTitle.html(`<span>📊</span> ${frappe.utils.escape_html(label)}`);

		const data = this.activeData || {};
		let contentHtml = `
      <div class="sod-modal-kpi-banner">
        <div>
          <div class="sod-modal-kpi-label">${frappe.utils.escape_html(label)}</div>
          <div class="sod-modal-kpi-val">${frappe.utils.escape_html(value)}</div>
        </div>
        <div style="font-size: 12px; color: #94a3b8; max-width: 260px; text-align: right;">
          ${frappe.utils.escape_html(
				desc || "Live metric calculated dynamically from ERPNext transactional records"
			)}
        </div>
      </div>
    `;

		// Form-Type details block
		const company = this.$el.find("#sod-filter-company").val() || "All Organizations";
		const dateRange = this.$el.find("#sod-filter-date").val() || "All Dates";
		const customer = this.$el.find("#sod-filter-customer").val() || "All Customers";
		const project = this.$el.find("#sod-filter-project").val() || "All Projects";

		contentHtml += `
      <div class="sod-form-block">
        <div class="sod-form-row">
          <span class="sod-form-label">Metric Name</span>
          <span class="sod-form-value">${frappe.utils.escape_html(label)}</span>
        </div>
        <div class="sod-form-row">
          <span class="sod-form-label">Current Value</span>
          <span class="sod-form-value" style="color: #2563eb;">${frappe.utils.escape_html(value)}</span>
        </div>
        <div class="sod-form-row">
          <span class="sod-form-label">Company Filter</span>
          <span class="sod-form-value">${frappe.utils.escape_html(company)}</span>
        </div>
        <div class="sod-form-row">
          <span class="sod-form-label">Date Filter</span>
          <span class="sod-form-value">${frappe.utils.escape_html(dateRange)}</span>
        </div>
        ${
			customer !== "All Customers"
				? `
          <div class="sod-form-row">
            <span class="sod-form-label">Customer Filter</span>
            <span class="sod-form-value">${frappe.utils.escape_html(customer)}</span>
          </div>
        `
				: ""
		}
        ${
			project !== "All Projects"
				? `
          <div class="sod-form-row">
            <span class="sod-form-label">Project Filter</span>
            <span class="sod-form-value">${frappe.utils.escape_html(project)}</span>
          </div>
        `
				: ""
		}
      </div>
    `;

		// Dynamic Related Records Table based on the Card
		const lblLower = label.toLowerCase();
		let hasRenderedCustomTable = false;

		// 1. If data.table exists (e.g. Projects Page, Sales Orders Page, Invoicing Page, etc.)
		if (data.table && data.table.headers && data.table.rows && data.table.rows.length) {
			const headers = data.table.headers;
			const rows = data.table.rows;

			const idIdx = headers.findIndex(
				(h) => /^id$/i.test(h) || /^name$/i.test(h) || /project/i.test(h)
			);
			const projIdx = headers.findIndex((h) => /^project$/i.test(h) || /project_name/i.test(h));
			const custIdx = headers.findIndex((h) => /customer/i.test(h));
			const statusIdx = headers.findIndex((h) => /status/i.test(h));
			const progressIdx = headers.findIndex(
				(h) => /%/i.test(h) || /complete/i.test(h) || /progress/i.test(h)
			);
			const budgetIdx = headers.findIndex((h) => /budget/i.test(h));
			const actualIdx = headers.findIndex((h) => /actual/i.test(h));
			const marginIdx = headers.findIndex(
				(h) => /margin/i.test(h) || /variance/i.test(h) || /billed/i.test(h)
			);
			const endIdx = headers.findIndex((h) => /end/i.test(h) || /due/i.test(h) || /date/i.test(h));

			let filteredRows = [];
			let displayHeaders = [];
			let rowMapper = null;
			let tableTitle = "Related Records";
			let badgeText = label;
			let badgeClass = "blue";

			if (
				lblLower.includes("active project") ||
				lblLower.includes("ongoing project") ||
				lblLower.includes("open project")
			) {
				tableTitle = "Active Projects Portfolio";
				badgeText = "Active / Ongoing";
				badgeClass = "blue";
				filteredRows = rows.filter((r) => {
					const st = String(statusIdx >= 0 ? r[statusIdx] : "").toLowerCase();
					return (
						st.includes("open") ||
						st.includes("active") ||
						st.includes("ongoing") ||
						(!st.includes("completed") && !st.includes("cancelled"))
					);
				});
				displayHeaders = [
					"PROJECT ID",
					"PROJECT NAME",
					"CUSTOMER",
					"STATUS",
					"% PROGRESS",
					"ESTIMATED BUDGET",
					"EXPECTED END",
				];
				rowMapper = (r) => {
					const idVal = r[idIdx >= 0 ? idIdx : 0];
					const pVal = r[projIdx >= 0 ? projIdx : 1] || idVal;
					const cVal = r[custIdx >= 0 ? custIdx : 2] || "—";
					const sVal = r[statusIdx >= 0 ? statusIdx : 4] || "Open";
					const prVal = r[progressIdx >= 0 ? progressIdx : 5] || "0%";
					const prNum = Math.min(
						100,
						Math.max(0, parseFloat(String(prVal).replace(/[^0-9.]/g, "")) || 0)
					);
					const bVal = r[budgetIdx >= 0 ? budgetIdx : 6] || "—";
					const eVal = r[endIdx >= 0 ? endIdx : 9] || "—";
					return [
						`<a href="javascript:void(0)" data-project-drill="${frappe.utils.escape_html(
							idVal
						)}" class="sod-link" style="font-weight:700;">${frappe.utils.escape_html(idVal)}</a>`,
						`<b>${frappe.utils.escape_html(pVal)}</b>`,
						frappe.utils.escape_html(cVal),
						`<span class="sod-pill blue">${frappe.utils.escape_html(sVal)}</span>`,
						`<div style="display:flex; align-items:center; gap:6px; min-width:85px;"><div style="flex:1; background:#e2e8f0; border-radius:10px; height:5px; overflow:hidden;"><div style="width:${prNum}%; background:#3b82f6; height:100%;"></div></div><b style="font-size:11px;">${prNum}%</b></div>`,
						`<b>${frappe.utils.escape_html(bVal)}</b>`,
						frappe.utils.escape_html(eVal),
					];
				};
			} else if (lblLower.includes("completed project") || lblLower.includes("delivered project")) {
				tableTitle = "Completed Projects Portfolio";
				badgeText = "Completed / Delivered";
				badgeClass = "green";
				filteredRows = rows.filter((r) => {
					const st = String(statusIdx >= 0 ? r[statusIdx] : "").toLowerCase();
					return st.includes("completed") || st.includes("delivered");
				});
				displayHeaders = [
					"PROJECT ID",
					"PROJECT NAME",
					"CUSTOMER",
					"STATUS",
					"% PROGRESS",
					"BUDGET",
					"ACTUAL COST",
					"NET MARGIN",
				];
				rowMapper = (r) => {
					const idVal = r[idIdx >= 0 ? idIdx : 0];
					const pVal = r[projIdx >= 0 ? projIdx : 1] || idVal;
					const cVal = r[custIdx >= 0 ? custIdx : 2] || "—";
					const sVal = r[statusIdx >= 0 ? statusIdx : 4] || "Completed";
					const prVal = r[progressIdx >= 0 ? progressIdx : 5] || "100%";
					const prNum = Math.min(
						100,
						Math.max(0, parseFloat(String(prVal).replace(/[^0-9.]/g, "")) || 100)
					);
					const bVal = r[budgetIdx >= 0 ? budgetIdx : 6] || "—";
					const aVal = r[actualIdx >= 0 ? actualIdx : 7] || "—";
					const mVal = r[marginIdx >= 0 ? marginIdx : 8] || "—";
					return [
						`<a href="javascript:void(0)" data-project-drill="${frappe.utils.escape_html(
							idVal
						)}" class="sod-link" style="font-weight:700;">${frappe.utils.escape_html(idVal)}</a>`,
						`<b>${frappe.utils.escape_html(pVal)}</b>`,
						frappe.utils.escape_html(cVal),
						`<span class="sod-pill green">${frappe.utils.escape_html(sVal)}</span>`,
						`<div style="display:flex; align-items:center; gap:6px; min-width:85px;"><div style="flex:1; background:#e2e8f0; border-radius:10px; height:5px; overflow:hidden;"><div style="width:100%; background:#10b981; height:100%;"></div></div><b style="font-size:11px;">${prNum}%</b></div>`,
						frappe.utils.escape_html(bVal),
						frappe.utils.escape_html(aVal),
						`<span style="color:#12b886; font-weight:700;">${frappe.utils.escape_html(
							mVal
						)}</span>`,
					];
				};
			} else if (lblLower.includes("budget")) {
				tableTitle = "Project Budget Allocation & Costing";
				badgeText = "Budget Breakdown";
				badgeClass = "purple";
				filteredRows = rows;
				displayHeaders = [
					"PROJECT ID",
					"PROJECT NAME",
					"CUSTOMER",
					"STATUS",
					"ESTIMATED BUDGET",
					"ACTUAL COST",
					"NET MARGIN",
				];
				rowMapper = (r) => {
					const idVal = r[idIdx >= 0 ? idIdx : 0];
					const pVal = r[projIdx >= 0 ? projIdx : 1] || idVal;
					const cVal = r[custIdx >= 0 ? custIdx : 2] || "—";
					const sVal = r[statusIdx >= 0 ? statusIdx : 4] || "—";
					const bVal = r[budgetIdx >= 0 ? budgetIdx : 6] || "—";
					const aVal = r[actualIdx >= 0 ? actualIdx : 7] || "—";
					const mVal = r[marginIdx >= 0 ? marginIdx : 8] || "—";
					return [
						`<a href="javascript:void(0)" data-project-drill="${frappe.utils.escape_html(
							idVal
						)}" class="sod-link" style="font-weight:700;">${frappe.utils.escape_html(idVal)}</a>`,
						`<b>${frappe.utils.escape_html(pVal)}</b>`,
						frappe.utils.escape_html(cVal),
						`<span class="sod-pill ${
							String(sVal).toLowerCase().includes("completed") ? "green" : "blue"
						}">${frappe.utils.escape_html(sVal)}</span>`,
						`<b style="color:#7950f2;">${frappe.utils.escape_html(bVal)}</b>`,
						frappe.utils.escape_html(aVal),
						`<span style="color:#12b886; font-weight:700;">${frappe.utils.escape_html(
							mVal
						)}</span>`,
					];
				};
			} else if (
				lblLower.includes("billed") ||
				lblLower.includes("revenue") ||
				lblLower.includes("invoice")
			) {
				tableTitle = "Project Billed Revenue Realization";
				badgeText = "Billing & Realization";
				badgeClass = "cyan";
				filteredRows = rows;
				displayHeaders = [
					"PROJECT ID",
					"PROJECT NAME",
					"CUSTOMER",
					"STATUS",
					"ESTIMATED BUDGET",
					"ACTUAL COST",
					"NET MARGIN",
				];
				rowMapper = (r) => {
					const idVal = r[idIdx >= 0 ? idIdx : 0];
					const pVal = r[projIdx >= 0 ? projIdx : 1] || idVal;
					const cVal = r[custIdx >= 0 ? custIdx : 2] || "—";
					const sVal = r[statusIdx >= 0 ? statusIdx : 4] || "—";
					const bVal = r[budgetIdx >= 0 ? budgetIdx : 6] || "—";
					const aVal = r[actualIdx >= 0 ? actualIdx : 7] || "—";
					const mVal = r[marginIdx >= 0 ? marginIdx : 8] || "—";
					return [
						`<a href="javascript:void(0)" data-project-drill="${frappe.utils.escape_html(
							idVal
						)}" class="sod-link" style="font-weight:700;">${frappe.utils.escape_html(idVal)}</a>`,
						`<b>${frappe.utils.escape_html(pVal)}</b>`,
						frappe.utils.escape_html(cVal),
						`<span class="sod-pill ${
							String(sVal).toLowerCase().includes("completed") ? "green" : "blue"
						}">${frappe.utils.escape_html(sVal)}</span>`,
						frappe.utils.escape_html(bVal),
						frappe.utils.escape_html(aVal),
						`<span style="color:#0284c7; font-weight:700;">${frappe.utils.escape_html(
							mVal
						)}</span>`,
					];
				};
			} else {
				// Other generic table pages
				tableTitle = `${label} Records`;
				badgeText = label;
				badgeClass = "blue";
				const cardWords = lblLower
					.replace(/[^a-z0-9 ]/g, "")
					.split(/\s+/)
					.filter((w) => w.length > 2);
				if (statusIdx >= 0) {
					const matched = rows.filter((r) => {
						const st = String(r[statusIdx] || "").toLowerCase();
						return cardWords.some((w) => st.includes(w));
					});
					filteredRows = matched.length ? matched : rows;
				} else {
					filteredRows = rows;
				}
				displayHeaders = headers.slice(0, 6);
				rowMapper = (r) =>
					r.slice(0, 6).map((c, ci) => {
						const s = String(c !== null && c !== undefined ? c : "—");
						if (ci === 0 && !s.includes("<")) return `<b>${frappe.utils.escape_html(s)}</b>`;
						return s.includes("<") ? s : frappe.utils.escape_html(s);
					});
			}

			contentHtml += `
				<div style="margin-top: 16px; border-top: 1px solid #e2e8f0; padding-top: 14px;">
					<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
						<div style="display:flex; align-items:center; gap:8px;">
							<h3 style="font-size: 13.5px; font-weight: 750; color: #1e293b; margin: 0; display:flex; align-items:center; gap:6px;">
								<span>📋</span> ${tableTitle} (${filteredRows.length})
							</h3>
							<span class="sod-pill ${badgeClass}" style="font-size: 11px;">${badgeText}</span>
						</div>
						<span style="font-size: 11.5px; color: #64748b;">Showing related details in full</span>
					</div>
					<div class="sod-modal-table-wrap">
						<table class="sod-table" style="width: 100%;">
							<thead>
								<tr>${displayHeaders.map((h) => `<th>${frappe.utils.escape_html(h)}</th>`).join("")}</tr>
							</thead>
							<tbody>
								${
									filteredRows.length
										? filteredRows
												.map(
													(r) =>
														`<tr>${rowMapper(r)
															.map((c) => `<td>${c}</td>`)
															.join("")}</tr>`
												)
												.join("")
										: `<tr><td colspan="${displayHeaders.length}" style="text-align:center; padding: 20px; color:#888;">No matching records found for this metric.</td></tr>`
								}
							</tbody>
						</table>
					</div>
				</div>
			`;
			hasRenderedCustomTable = true;
		}

		// 2. If data.active_projects exists (Overview dashboard or similar) and not rendered yet
		if (!hasRenderedCustomTable && (action === "view-projects" || lblLower.includes("project"))) {
			let projs = data.active_projects || [];
			if (lblLower.includes("completed")) {
				projs = projs.filter((p) => (p.status || "").toLowerCase() === "completed");
			} else if (lblLower.includes("active") || lblLower.includes("open")) {
				projs = projs.filter(
					(p) =>
						(p.status || "").toLowerCase() !== "completed" &&
						(p.status || "").toLowerCase() !== "cancelled"
				);
			}
			if (projs.length) {
				contentHtml += `
          <div style="margin-top: 16px; border-top: 1px solid #e2e8f0; padding-top: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
              <h3 style="font-size: 13.5px; font-weight: 750; color: #1e293b; margin: 0; display:flex; align-items:center; gap:6px;">
                <span>📋</span> Matching Projects (${projs.length})
              </h3>
              <span class="sod-pill blue" style="font-size: 11px;">${frappe.utils.escape_html(label)}</span>
            </div>
            <div class="sod-modal-table-wrap">
              <table class="sod-table" style="width: 100%;">
                <thead><tr><th>PROJECT</th><th>CUSTOMER</th><th>STATUS</th><th>PROGRESS</th><th>BUDGET</th></tr></thead>
                <tbody>
                  ${projs
						.map(
							(p) => `
                    <tr>
                      <td><a href="javascript:void(0)" data-project-drill="${frappe.utils.escape_html(
							p.project
						)}" class="sod-link" style="font-weight:700;">${frappe.utils.escape_html(
								p.project_name || p.project
							)}</a></td>
                      <td>${frappe.utils.escape_html(p.customer || "—")}</td>
                      <td><span class="sod-pill ${
							p.status === "Completed" ? "green" : "blue"
						}">${frappe.utils.escape_html(p.status)}</span></td>
                      <td><b>${flt(p.percent_complete || 0)}%</b></td>
                      <td>${frappe.utils.escape_html(p.budget || "—")}</td>
                    </tr>
                  `
						)
						.join("")}
                </tbody>
              </table>
            </div>
          </div>
        `;
				hasRenderedCustomTable = true;
			}
		}

		// 3. If data.sales_orders exists (Commercial Order Book, Overview, etc.) and not rendered yet
		if (
			!hasRenderedCustomTable &&
			(action === "view-sales-orders" || lblLower.includes("order") || lblLower.includes("commercial"))
		) {
			const sos = data.sales_orders || [];
			if (sos.length) {
				contentHtml += `
          <div style="margin-top: 16px; border-top: 1px solid #e2e8f0; padding-top: 14px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
              <h3 style="font-size: 13.5px; font-weight: 750; color: #1e293b; margin: 0; display:flex; align-items:center; gap:6px;">
                <span>📋</span> Matching Sales Orders (${sos.length})
              </h3>
              <span class="sod-pill blue" style="font-size: 11px;">${frappe.utils.escape_html(label)}</span>
            </div>
            <div class="sod-modal-table-wrap">
              <table class="sod-table" style="width: 100%;">
                <thead><tr><th>ORDER ID</th><th>CUSTOMER</th><th>AMOUNT</th><th>% DELIVERED</th><th>STATUS</th></tr></thead>
                <tbody>
                  ${sos
						.map(
							(s) => `
                    <tr>
                      <td><a href="/app/sales-order/${encodeURIComponent(
							s[0]
						)}" target="_blank" class="sod-link"><b>${frappe.utils.escape_html(s[0])}</b></a></td>
                      <td>${frappe.utils.escape_html(s[1])}</td>
                      <td>${frappe.utils.escape_html(s[2])}</td>
                      <td>${frappe.utils.escape_html(s[3])}</td>
                      <td><span class="sod-pill blue">${frappe.utils.escape_html(
							s[6] || s[5] || "Active"
						)}</span></td>
                    </tr>
                  `
						)
						.join("")}
                </tbody>
              </table>
            </div>
          </div>
        `;
				hasRenderedCustomTable = true;
			}
		}

		// 4. Stock & Quality Widgets
		if (
			!hasRenderedCustomTable &&
			(action === "view-stock" || lblLower.includes("stock") || lblLower.includes("capital"))
		) {
			const cap = data.capital_allocation || {};
			const lowStock = data.low_stock_items || [];
			contentHtml += `
        <div class="sod-form-block" style="margin-top: 10px;">
          <div class="sod-form-row"><span class="sod-form-label">Raw Materials (RM)</span><span class="sod-form-value">${
				cap.rm_val || "₹0"
			} (${cap.rm_pct || 0}%)</span></div>
          <div class="sod-form-row"><span class="sod-form-label">Work In Progress (WIP)</span><span class="sod-form-value">${
				cap.wip_val || "₹0"
			} (${cap.wip_pct || 0}%)</span></div>
          <div class="sod-form-row"><span class="sod-form-label">Finished Goods (FG)</span><span class="sod-form-value">${
				cap.fg_val || "₹0"
			} (${cap.fg_pct || 0}%)</span></div>
          <div class="sod-form-row"><span class="sod-form-label">Total Inventory Valuation</span><span class="sod-form-value" style="color:#8a54ef;">${
				cap.total_val || "₹0"
			}</span></div>
        </div>
      `;
			if (lowStock.length) {
				contentHtml += `
          <h3 style="font-size: 13px; font-weight: 700; margin: 12px 0 6px; color: #e11d48;">Reorder Level Alerts (${
				lowStock.length
			})</h3>
          <div class="sod-modal-table-wrap">
            <table class="sod-table">
              <thead><tr><th>ITEM</th><th>WAREHOUSE</th><th>AVAILABLE</th><th>REORDER QTY</th></tr></thead>
              <tbody>
                ${lowStock
					.map(
						(l) => `
                  <tr>
                    <td><a href="/app/item/${encodeURIComponent(
						l.item_code
					)}" target="_blank" class="sod-link"><b>${frappe.utils.escape_html(
							l.item_name
						)}</b></a></td>
                    <td>${frappe.utils.escape_html(l.warehouse)}</td>
                    <td><span style="color:#e11d48; font-weight:700;">${frappe.utils.escape_html(
						l.available
					)}</span></td>
                    <td>${frappe.utils.escape_html(l.reorder)}</td>
                  </tr>
                `
					)
					.join("")}
              </tbody>
            </table>
          </div>
        `;
			}
		} else if (
			!hasRenderedCustomTable &&
			(action === "view-finance" ||
				action === "view-pnl" ||
				action === "view-reports" ||
				lblLower.includes("profit") ||
				lblLower.includes("receivable") ||
				lblLower.includes("cost"))
		) {
			const snap = data.financial_snapshot || {};
			contentHtml += `
        <div class="sod-form-block" style="margin-top: 10px;">
          <div class="sod-form-row"><span class="sod-form-label">Total Revenue / Income</span><span class="sod-form-value" style="color:#12b886;">${
				snap.income || "₹0"
			}</span></div>
          <div class="sod-form-row"><span class="sod-form-label">Operating Expenses</span><span class="sod-form-value" style="color:#e11d48;">${
				snap.expenses || "₹0"
			}</span></div>
          <div class="sod-form-row"><span class="sod-form-label">Net Profit Realized</span><span class="sod-form-value" style="color:#2563eb; font-size:14px;">${
				snap.net_profit || "₹0"
			}</span></div>
          <div class="sod-form-row"><span class="sod-form-label">Accounts Receivable</span><span class="sod-form-value">${
				snap.receivables || "₹0"
			}</span></div>
          <div class="sod-form-row"><span class="sod-form-label">Overdue Receivables</span><span class="sod-form-value" style="color:#e11d48;">${
				snap.overdue || "₹0"
			}</span></div>
        </div>
      `;
		}

		this.$modalBody.html(contentHtml);

		// Footer buttons (Open in Desk button removed)
		let navActionBtn = "";
		const self = this;
		if (action === "view-projects") {
			navActionBtn = `<button class="sod-btn-primary" style="background:#5369ef;" id="sod-modal-nav-action">Open Projects View ▦</button>`;
		} else if (action === "view-sales-orders") {
			navActionBtn = `<button class="sod-btn-primary" style="background:#0284c7;" id="sod-modal-nav-action">Open Orders View ▣</button>`;
		} else if (action === "view-finance") {
			navActionBtn = `<button class="sod-btn-primary" style="background:#16a34a;" id="sod-modal-nav-action">Open Invoicing View ₹</button>`;
		} else if (action === "view-stock") {
			navActionBtn = `<button class="sod-btn-primary" style="background:#9333ea;" id="sod-modal-nav-action">Open Inventory View ◫</button>`;
		}

		this.$modalFoot.html(`
      <button class="sod-btn-sm" style="background:#fff; border:1px solid #cbd5e1; color:#334155; padding:8px 16px; border-radius:7px; font-weight:600; cursor:pointer;" id="sod-modal-foot-close">Close</button>
      ${navActionBtn}
    `);

		this.$modalFoot.find("#sod-modal-foot-close").on("click", () => this.$modal.removeClass("show"));
		this.$modalFoot.find("#sod-modal-nav-action").on("click", () => {
			this.$modal.removeClass("show");
			if (action === "view-projects") self.goToPageByKey("projects");
			else if (action === "view-sales-orders") self.goToPageByKey("sales_orders");
			else if (action === "view-finance") self.goToPageByKey("invoicing");
			else if (action === "view-stock") self.goToPageByKey("stock_quality");
		});

		this.$modal.addClass("show");
	}

	showStageModal(projectName, stageId) {
		const pipelineData = (this.activeData?.pipelines || []).find((p) => p.project === projectName) ||
			this.activeData?.pipeline || { project: projectName, project_name: projectName };

		const stages = this.resolvePipelineStages(pipelineData);
		const stage = stages.find((s) => s.id === stageId);
		if (!stage) return;

		this.$modalTitle.text(`${stage.label} · ${pipelineData.project_name || projectName}`);

		let recordsHtml = "";
		if (stage.records && stage.records.length) {
			recordsHtml = stage.records
				.map(
					(rec) =>
						`<li><a href="/app/${encodeURIComponent(
							stage.doctype.toLowerCase().replace(/ /g, "-")
						)}/${encodeURIComponent(
							rec
						)}" target="_blank" class="sod-link" style="font-size:12.5px;">${frappe.utils.escape_html(
							rec
						)} ↗</a></li>`
				)
				.join("");
		} else {
			recordsHtml = `<li><em>No ${stage.doctype} records recorded (${stage.badge}).</em></li>`;
		}

		const statusPillClass =
			stage.status === "done"
				? "green"
				: stage.status === "current"
				? "purple"
				: stage.status === "fail"
				? "red"
				: "blue";

		this.$modalBody.html(`
      <p style="font-size:13px; margin-bottom:10px;">
        <b>DocType:</b> ${stage.doctype} &nbsp;|&nbsp;
        <b>In-Charge:</b> <span style="color:#4f46e5; font-weight:750;">👤 ${frappe.utils.escape_html(
			stage.in_charge || "Operations"
		)}</span> &nbsp;|&nbsp;
        <b>Department:</b> ${frappe.utils.escape_html(stage.department || "Operations")} &nbsp;|&nbsp;
        <b>Customer:</b> ${frappe.utils.escape_html(pipelineData.customer)}
      </p>
      <div class="sod-modal-box">
        <b>Stage Status:</b> <span class="sod-pill ${statusPillClass}">${stage.status.toUpperCase()}</span><br>
        <b>Summary:</b> ${frappe.utils.escape_html(stage.badge)}<br>
        <b>Phase:</b> ${frappe.utils.escape_html(stage.phase || "Process Flow")}<br>
        <b>Description:</b> ${frappe.utils.escape_html(stage.info)}<br>
        <b>Linked Records (${stage.count}):</b>
        <ul style="margin: 8px 0 0 16px; padding: 0;">${recordsHtml}</ul>
      </div>
      <p style="font-size: 11.5px; color: #7788a0; margin-top:8px;">Clicking any record opens the native ERPNext document in Desk.</p>
    `);

		this.$modalFoot.html(`
      <button class="sod-btn-sm" style="background:#fff; border:1px solid #cbd5e1; color:#334155; padding:8px 16px; border-radius:7px; font-weight:600; cursor:pointer;" id="sod-modal-stage-close">Close</button>
      <a class="sod-btn-primary" href="/app/${encodeURIComponent(
			stage.doctype.toLowerCase().replace(/ /g, "-")
		)}?project=${encodeURIComponent(projectName)}" target="_blank">
        View All ${stage.doctype}s ↗
      </a>
    `);
		this.$modalFoot.find("#sod-modal-stage-close").on("click", () => this.$modal.removeClass("show"));

		this.$modal.addClass("show");
	}

	show() {
		this.visible = true;
		window.scrollTo(0, 0);

		if (typeof localStorage !== "undefined") {
			try {
				localStorage.removeItem("_page:sarathiownertower");
				localStorage.removeItem("page:sarathiownertower");
				localStorage.removeItem("route:sarathiownertower");
			} catch (e) {
				// Local storage might be restricted in certain browser contexts
			}
		}

		// Purge any rogue duplicate wrappers or footers
		if (this.root) {
			$(".sod-wrapper").not(this.root).remove();
			$(".sod-footer").remove();
			$(".sod-wrapper ~ .sod-wrapper").remove();
		}

		// Clear cached dataset to ensure fresh reload
		this.activeData = null;

		// Sync with route or URL tab parameter if present
		const urlParams = new URLSearchParams(window.location.search);
		const tabParam = urlParams.get("tab");
		if (tabParam) {
			const targetIdx = this.pagesConfig.findIndex((p) => p[3] === tabParam);
			if (targetIdx >= 0 && targetIdx !== this.currentPage) {
				this.selectPage(targetIdx);
				return;
			}
		}

		this.refreshFilterDropdownsOnly();
		this.refreshCurrentPage();
		setTimeout(() => window.dispatchEvent(new Event("resize")), 100);
		if (!this.refreshTimer) {
			// 15-second background sync interval
			this.refreshTimer = setInterval(() => {
				if (document.hidden) return;
				this.smoothRefresh();
			}, 15000);
		}
	}

	hide() {
        Object.values(this.chartResizeDisposers || {}).forEach(dispose => dispose());
        this.chartResizeDisposers = {};
		this.visible = false;
		this.pageRequest = (this.pageRequest || 0) + 1;
		if (this.refreshTimer) {
			clearInterval(this.refreshTimer);
			this.refreshTimer = null;
		}
	}
};

// Nested finance cards stay inside the owner dashboard.  This override replaces
// the old optional module-browser handoff, which could open an ERPNext screen.
frappe.SarathiOwnerDashboard.prototype.showQuickDetails = function (action) {
	const esc = (value) => frappe.utils.escape_html(String(value ?? "—"));
	const dialog = new frappe.ui.Dialog({
		title: (action.label || "Details").replace(/\s*\(\+ New\)/i, "").replace(/^New /, ""),
		size: "extra-large",
		fields: [{ fieldtype: "HTML", fieldname: "details" }],
	});
	dialog.$wrapper.addClass("sod-detail-dialog");
	const host = dialog.fields_dict.details.$wrapper;
	const filters = this.getFilters();
	let offset = 0,
		search = "",
		activeName = null,
		requestNumber = 0,
		timer;
	const format = (value, type) => {
		if (value === null || value === undefined || value === "") return "—";
		if (["Currency", "Float", "Int", "Percent"].includes(type) && Number.isFinite(Number(value))) {
			return (
				new Intl.NumberFormat("en-IN", { maximumFractionDigits: type === "Int" ? 0 : 2 }).format(
					Number(value)
				) + (type === "Percent" ? "%" : "")
			);
		}
		return typeof value === "object" ? JSON.stringify(value) : value;
	};
	const renderTable = (columns, rows, clickable) =>
		`<div class="sod-quick-table"><table><thead><tr>${columns
			.map((c) => `<th>${esc(c.label)}</th>`)
			.join("")}</tr></thead><tbody>${rows
			.map(
				(row, index) =>
					`<tr>${columns
						.map(
							(c, cell) =>
								`<td>${
									clickable && cell === 0
										? `<button type="button" data-detail-record="${index}">${esc(
												row.name
										  )}</button>`
										: esc(
												format(
													Array.isArray(row) ? row[cell] : row[c.fieldname],
													c.fieldtype
												)
										  )
								}</td>`
						)
						.join("")}</tr>`
			)
			.join("")}</tbody></table></div>`;
	const load = async (name = null) => {
		activeName = name;
		const currentRequest = ++requestNumber;
		host.html('<div class="sod-quick-loading" role="status">Loading live details and analysis…</div>');
		try {
			const response = await frappe.call({
				method: "sarathi_owner.api.quick_details.get_details",
				args: {
					route: action.route,
					entry_id: action.id,
					label: action.label,
					kind: action.kind,
					target: action.target,
					filters: JSON.stringify(filters),
					search,
					start: offset,
					name,
				},
			});
			if (currentRequest !== requestNumber) return;
			const data = response.message || {};
			dialog.set_title(esc(action.label || data.label || data.doctype));
			host.html(
				`<div class="sod-quick-toolbar"><span class="sod-quick-tag">${esc(
					data.doctype || data.label || action.label
				)}</span><span>Updated ${esc(
					new Date().toLocaleTimeString()
				)}</span><button type="button" data-detail-refresh>Refresh</button>${
					name ? '<button type="button" data-detail-back>← Back</button>' : ""
				}</div>`
			);
			host.find("[data-detail-refresh]").on("click", () => load(activeName));
			host.find("[data-detail-back]").on("click", () => {
				offset = 0;
				search = "";
				load();
			});
			if (data.scope_note) host.append(`<p class="sod-detail-note">${esc(data.scope_note)}</p>`);
			if (data.error || data.restricted) {
				host.append(`<p class="sod-quick-empty">${esc(data.message || data.error)}</p>`);
				return;
			}
			const cards = data.calculations || data.highlights || [];
			if (cards.length)
				host.append(
					`<div class="sod-detail-metrics">${cards
						.map(
							(card) =>
								`<article><small>${esc(card.label)}</small><strong>${esc(
									format(card.value, card.fieldtype)
								)}</strong><p>${esc(card.desc || "")}</p></article>`
						)
						.join("")}</div>`
				);
			const charts = data.charts || [];
			if (charts.length) {
				host.append(
					`<div class="sod-detail-charts">${charts
						.map(
							(chart, index) =>
								`<section><h4>${esc(
									chart.title || "Analysis"
								)}</h4><div data-detail-chart="${index}"></div></section>`
						)
						.join("")}</div>`
				);
				const drawCharts = () =>
					charts.forEach(
						(chart, index) =>
							new frappe.Chart(host.find(`[data-detail-chart="${index}"]`)[0], {
								data: chart.data || { labels: chart.labels, datasets: chart.datasets },
								type: chart.type || "bar",
								height: 220,
								colors: [
									"#4f46e5",
									"#0ea5a4",
									"#f59e0b",
									"#ec4899",
									"#8b5cf6",
									"#16a34a",
									"#ef4444",
								],
								truncateLegends: 1,
							})
					);
				frappe.Chart ? drawCharts() : frappe.require("frappe-charts.bundle.js", drawCharts);
			}
			if (data.kind === "workspace") {
				host.append(
					`<div class="sod-detail-entries">${
						(data.entries || [])
							.map(
								(entry, index) =>
									`<button type="button" data-detail-entry="${index}"><small>${esc(
										entry.section || entry.kind
									)}</small><strong>${esc(
										entry.label
									)}</strong><span>Open details</span></button>`
							)
							.join("") || "<p>No entries are available for your permissions.</p>"
					}</div>`
				);
				host.find("[data-detail-entry]").on("click", (event) => {
					Object.assign(action, data.entries[Number(event.currentTarget.dataset.detailEntry)]);
					offset = 0;
					search = "";
					load();
				});
				return;
			}
			if (data.kind === "record") {
				host.append(
					`<h3>${esc(data.name)}</h3><div class="sod-quick-fields">${(data.fields || [])
						.map(
							(field) =>
								`<div><small>${esc(field.label)}</small><strong>${esc(
									format(field.value, field.fieldtype)
								)}</strong></div>`
						)
						.join("")}</div>`
				);
				(data.tables || []).forEach((table) =>
					host.append(
						`<h4>${esc(table.label)} · ${table.total}</h4>${
							table.rows.length
								? renderTable(table.columns, table.rows, false)
								: "<p>No saved rows.</p>"
						}`
					)
				);
				return;
			}
			const columns = data.columns || [],
				rows = data.result || [];
			host.append(
				`<label class="sod-quick-search">Search matching records<input type="search" value="${esc(
					search
				)}" placeholder="Name or ID"></label>${renderTable(
					columns,
					rows,
					true
				)}<div class="sod-quick-footer"><span>${data.total_count || 0} matching records · ${
					rows.length ? offset + 1 : 0
				}–${offset + rows.length} shown</span><button data-detail-prev ${
					offset ? "" : "disabled"
				}>Previous</button><button data-detail-next ${
					data.has_more ? "" : "disabled"
				}>Next</button></div>`
			);
			if (!rows.length)
				host.append('<p class="sod-quick-empty">No matching records for these filters.</p>');
			host.find("[data-detail-record]").on("click", (event) =>
				load(rows[Number(event.currentTarget.dataset.detailRecord)].name)
			);
			host.find("[data-detail-prev]").on("click", () => {
				offset = Math.max(0, offset - 25);
				load();
			});
			host.find("[data-detail-next]").on("click", () => {
				offset += 25;
				load();
			});
			host.find('input[type="search"]').on("input", (event) => {
				search = event.target.value;
				clearTimeout(timer);
				timer = setTimeout(() => {
					offset = 0;
					load();
				}, 400);
			});
		} catch (_) {
			if (currentRequest === requestNumber)
				host.html(
					'<p class="sod-quick-empty" role="alert">Details could not be loaded. Please retry.</p><button data-detail-retry>Retry</button>'
				);
			host.find("[data-detail-retry]").on("click", () => load(name));
		}
	};
	dialog.onhide = () => {
		requestNumber++;
		clearTimeout(timer);
		dialog.$wrapper.remove();
	};
	dialog.show();
	load();
};
