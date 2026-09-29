/* Sarathi Owner Dashboard - Frontend Controller
   Live Reports, Interactive Frappe Charts, Real-Time Socket.IO Updates, and Live Changing Values.
*/

frappe.provide("frappe.SarathiOwnerDashboard");

frappe.SarathiOwnerDashboard = class {
  constructor(wrapper) {
    this.wrapper = $(wrapper);
    // Purge any existing DOM nodes from wrapper before building page
    this.wrapper.empty();

    this.page = frappe.ui.make_app_page({
      parent: wrapper,
      title: "Sarathi Owner Dashboard",
      single_column: true,
    });

    this.page.main.empty();
    this.root = $(frappe.render_template("sarathiownertower", {})).appendTo(
      this.page.main,
    )[0];

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
    this.accountingDropdownOpen = false;

    document.documentElement.classList.add("sod-page-active");
    document.body.classList.add("sod-page-active");
    $(".main-section").scrollTop(0);
    window.scrollTo(0, 0);

    this.initElements();
    this.bindEvents();
    this.initRealtimeListener();
    this.renderNav();
    this.loadContext();
  }

  initElements() {
    this.$el = $(this.root);
    this.$nav = this.$el.find("#sod-nav");
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
    this.$el
      .find("#sod-live-time")
      .text(now.toLocaleDateString("en-IN", options));

    // User Avatar Initials
    const fullName =
      frappe.session.user_fullname || frappe.session.user || "Owner";
    const initials = fullName
      .split(" ")
      .map((n) => n[0])
      .join("")
      .substring(0, 2)
      .toUpperCase();
    this.$el.find("#sod-avatar-initials").text(initials || "OW");
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
          ].includes(data.doctype)
        ) {
          self.handleLiveSocketChange(data);
        }
      });
    }
  }

  handleLiveSocketChange(data) {
    const dt = data.doctype || "Transaction";
    const name = data.name || "";
    this.showLiveToast(`⚡ Live Update: ${dt} ${name} updated`);

    // Dynamically refresh the dropdown options if a Company, Customer, or Project was modified
    if (["Company", "Customer", "Project"].includes(dt)) {
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
    this.$el.on("click", "[data-action='refresh']", function () {
      const $btn = $(this);
      $btn.addClass("sod-spinning");
      self.refreshCurrentPage();
      setTimeout(() => $btn.removeClass("sod-spinning"), 600);
    });

    // Quick Live Report Button
    this.$el.on("click", "[data-action='run-quick-report']", function () {
      self.goToPageByKey("reports");
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

    // Global Reactive Filters
    this.$el.find("#sod-filter-company").on("change", function () {
      self.populateFilterDropdowns();
      self.refreshCurrentPage();
    });

    this.$el
      .find(
        "#sod-filter-date, #sod-filter-customer, #sod-filter-project, #sod-filter-status",
      )
      .on("change", function () {
        self.refreshCurrentPage();
      });

    let searchTimeout = null;
    this.$el.find("#sod-search-input").on("input", function () {
      clearTimeout(searchTimeout);
      searchTimeout = setTimeout(() => {
        self.refreshCurrentPage();
      }, 300);
    });

    // Interactive Card Click Handlers
    this.$content.on("click", ".sod-card[data-action]", function () {
      const action = $(this).data("action");
      if (action === "view-projects") {
        self.goToPageByKey("projects");
      } else if (action === "view-sales-orders") {
        self.goToPageByKey("sales_orders");
      } else if (action === "view-finance") {
        self.goToPageByKey("invoicing");
      } else if (action === "view-stock") {
        self.goToPageByKey("stock_quality");
      } else if (action === "view-reports") {
        self.goToPageByKey("reports");
      } else if (action === "open-live-report") {
        const rep = $(this).data("report");
        if (rep) {
          self.currentReportName = rep;
          self.goToPageByKey("reports");
        }
      } else if (action === "open-desk") {
        const route = $(this).data("route");
        if (route) window.open(route, "_blank");
      }
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

    // Activity Item Click
    this.$content.on("click", ".sod-activity-item[data-route]", function () {
      const route = $(this).data("route");
      if (route) window.open(route, "_blank");
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
        <button class="${idx === this.currentPage ? "active" : ""}" data-page="${idx}" data-key="${frappe.utils.escape_html(pageKey || "")}" title="${frappe.utils.escape_html(title)}">
          <span class="sod-icon">${icon}</span>
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
    const selectedCompany = this.$el.find("#sod-filter-company").val() || "";

    // Companies
    const $co = this.$el.find("#sod-filter-company");
    const currentCo = $co.val();
    $co.find("option:not(:first)").remove();
    (this.context.companies || []).forEach((c) => {
      $co.append(
        `<option value="${frappe.utils.escape_html(c.name)}">${frappe.utils.escape_html(c.company_name || c.name)}</option>`,
      );
    });
    if (currentCo) $co.val(currentCo);

    // Customers
    const $cust = this.$el.find("#sod-filter-customer");
    const currentCust = $cust.val();
    $cust.find("option:not(:first)").remove();
    (this.context.customers || []).forEach((c) => {
      $cust.append(
        `<option value="${frappe.utils.escape_html(c.name)}">${frappe.utils.escape_html(c.customer_name || c.name)}</option>`,
      );
    });
    if (currentCust) $cust.val(currentCust);

    // Projects (Dynamically filtered by selected company)
    const $proj = this.$el.find("#sod-filter-project");
    const currentProj = $proj.val();
    $proj.find("option:not(:first)").remove();
    (this.context.projects || [])
      .filter((p) => !selectedCompany || p.company === selectedCompany)
      .forEach((p) => {
        $proj.append(
          `<option value="${frappe.utils.escape_html(p.name)}">${frappe.utils.escape_html(p.project_name || p.name)}</option>`,
        );
      });
    if (currentProj && $proj.find(`option[value="${currentProj}"]`).length) {
      $proj.val(currentProj);
    }
  }

  getFilters() {
    return {
      company: this.$el.find("#sod-filter-company").val() || "",
      date_range: this.$el.find("#sod-filter-date").val() || "all",
      customer: this.$el.find("#sod-filter-customer").val() || "",
      project:
        this.$el.find("#sod-filter-project").val() ||
        this.selectedProject ||
        "",
      status: this.$el.find("#sod-filter-status").val() || "",
      search: this.$el.find("#sod-search-input").val() || "",
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

    this.$breadcrumb.text(title);
    this.$title.text(idx === 0 ? "Sarathi Owner Overview" : title);
    this.$subtitle.text(subtitle);

    this.refreshCurrentPage();
  }

  /* -------------------------------------------------------------
     DATA REFRESH: Full reload vs. Smooth Live Updating
  ------------------------------------------------------------- */
  refreshCurrentPage() {
    this.chartInstances = {};

    this.$content.html(`
      <div class="sod-loading">
        <div class="sod-spinner"></div>
        <p>Connecting to ERPNext and aggregating real-time metrics…</p>
      </div>
    `);

    const filters = this.getFilters();
    const config = this.pagesConfig[this.currentPage] || this.pagesConfig[0];
    const pageKey = config[3] || "home";

    if (pageKey === "home") {
      frappe.call({
        method: "sarathi_owner.api.owner_dashboard.get_owner_summary",
        args: { filters: JSON.stringify(filters) },
        callback: (r) => {
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
        callback: (r) => {
          this.activeData = r.message || {};
          this.renderGenericPage(this.currentPage, this.activeData);
        },
      });
    }
  }

  smoothRefresh() {
    const filters = this.getFilters();
    const config = this.pagesConfig[this.currentPage] || this.pagesConfig[0];
    const pageKey = config[3] || "home";

    if (pageKey === "home") {
      frappe.call({
        method: "sarathi_owner.api.owner_dashboard.get_owner_summary",
        args: { filters: JSON.stringify(filters) },
        callback: (r) => {
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
        callback: (r) => {
          if (!r.message) return;
          this.activeData = r.message;
          this.renderGenericPage(this.currentPage, this.activeData);
        },
      });
    }
  }

  /* -------------------------------------------------------------
     RENDERER: Page 0 (Owner Home)
  ------------------------------------------------------------- */
  renderOwnerHome(data) {
    const cards = data.cards || [];
    const pipelines = data.pipelines || [];
    const alerts = data.action_alerts || [];
    const liveActivity = data.live_activity || [];
    const activeProjects = data.active_projects || [];
    const capital = data.capital_allocation || {};

    let html = "";

    // 1. KPI Cards (Top Executive Metrics with Clickable Drill-Downs)
    html += '<div class="sod-grid sod-cards" id="sod-kpi-cards-grid">';
    cards.forEach((c) => {
      html += `
        <div class="sod-card ${c.color}" data-action="${frappe.utils.escape_html(c.action || "")}" role="button" tabindex="0" title="Click to drill down">
          <div class="sod-label">${frappe.utils.escape_html(c.label)}</div>
          <strong class="sod-kpi-val">${frappe.utils.escape_html(c.value)}</strong>
          <small>${frappe.utils.escape_html(c.desc || "ERPNext records")}</small>
          <span class="sod-card-arrow">↗</span>
        </div>
      `;
    });
    html += "</div>";

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

    // 4. Strategic Manufacturing Pipeline Section
    html += `
      <section class="sod-panel" style="margin-top: 17px;">
        <div class="sod-panel-head">
          <div>
            <h2>Strategic Manufacturing Pipeline · Active Projects</h2>
            <p>Click any stage circle to inspect linked ERPNext records and live execution status</p>
          </div>
        </div>
        <div class="sod-pipeline-container">
    `;

    if (!pipelines.length) {
      html +=
        '<div class="sod-empty">No active in-progress manufacturing projects found matching filters.</div>';
    } else {
      pipelines.forEach((p) => {
        html += `
          <div class="sod-portfolio-row" data-project="${frappe.utils.escape_html(p.project)}">
            <div class="sod-portfolio-head">
              <b><a href="/app/project/${encodeURIComponent(p.project)}" target="_blank" class="sod-link">${frappe.utils.escape_html(p.project_name)}</a></b>
              <span>${frappe.utils.escape_html(p.customer)} · <b>${frappe.utils.escape_html(p.project)}</b> · ${p.percent_complete}% Milestone · <b>${p.manufacturing_progress}% Output</b></span>
            </div>
            ${this.renderPipelineMarkup(p)}
          </div>
        `;
      });
    }
    html += `
        </div>
      </section>
    `;

    // 5. Two-Column Grid: Active Projects Table & Live Activity Feed
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
        html += `
          <tr class="sod-clickable-row" data-project-drill="${frappe.utils.escape_html(row.project)}">
            <td><a href="/app/project/${encodeURIComponent(row.project)}" target="_blank" class="sod-link">${frappe.utils.escape_html(row.project_name)}</a></td>
            <td><a href="/app/customer/${encodeURIComponent(row.customer)}" target="_blank" class="sod-link">${frappe.utils.escape_html(row.customer)}</a></td>
            <td><b>${row.percent_complete}%</b> <small style="color:#778899;">(${frappe.utils.escape_html(row.wo_output)})</small></td>
            <td>${frappe.utils.escape_html(row.budget)}</td>
            <td>${frappe.utils.escape_html(row.actual_cost)}</td>
            <td>${frappe.utils.escape_html(row.expected_end_date)}</td>
            <td><span class="sod-pill ${row.schedule_status === "Delayed" ? "red" : "green"}">${row.schedule_status}</span></td>
            <td><button class="sod-btn-sm" data-project-drill="${frappe.utils.escape_html(row.project)}" title="Drill into Project Details">View ▤</button></td>
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
            <h2>Real-Time Business Events <span class="sod-live-status-pill"><span class="sod-pulse-dot"></span> LIVE</span></h2>
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
          <div class="sod-activity-item" data-route="${frappe.utils.escape_html(act.route || "")}" title="Click to view document in Desk">
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
    $target.empty();

    try {
      if (window.frappe && frappe.Chart) {
        const chart = new frappe.Chart($target[0], {
          data: options.data || { labels: [], datasets: [] },
          type: options.type || "bar",
          height: options.height || 220,
          colors: options.colors || [
            "#5369ef",
            "#12b886",
            "#f2a342",
            "#e03131",
          ],
          barOptions: options.barOptions || { spaceRatio: 0.3 },
          axisOptions: { xIsSeries: true },
          tooltipOptions: {
            formatTooltipX: (d) => (d + "").toUpperCase(),
            formatTooltipY: (d) =>
              typeof d === "number" ? "₹" + d.toLocaleString("en-IN") : d,
          },
        });
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
      if (
        this.chartInstances["#sod-chart-financial"] &&
        newData.charts.financial
      ) {
        this.chartInstances["#sod-chart-financial"].update(
          newData.charts.financial,
        );
      }
      if (this.chartInstances["#sod-chart-capital"] && newData.charts.capital) {
        this.chartInstances["#sod-chart-capital"].update(
          newData.charts.capital,
        );
      }
      if (
        this.chartInstances["#sod-chart-orderbook"] &&
        newData.charts.order_book
      ) {
        this.chartInstances["#sod-chart-orderbook"].update(
          newData.charts.order_book,
        );
      }
      if (
        this.chartInstances["#sod-chart-ar-aging"] &&
        newData.charts.ar_aging
      ) {
        this.chartInstances["#sod-chart-ar-aging"].update(
          newData.charts.ar_aging,
        );
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
      [
        "Warehouse Wise Stock Balance",
        "Working capital valuation across warehouses",
        "Stock",
        "◫",
      ],
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
      html += `<option value="${frappe.utils.escape_html(name)}" data-icon="${icon}" data-desc="${frappe.utils.escape_html(desc)}" ${selected}>${icon} ${frappe.utils.escape_html(name)} (${type})</option>`;
    });

    html += `
            </select>
            <input type="search" id="sod-report-search" class="sod-input" placeholder="Filter rows in report..." style="width: 160px; max-width: 100%;">
            <button class="sod-btn-sm" id="sod-btn-refresh-report" title="Rerun report query">↻ Run Live</button>
            <button class="sod-btn-sm" id="sod-btn-export-csv" title="Download CSV of current table">⬇ Export CSV</button>
            <a href="/app/query-report/${encodeURIComponent(this.currentReportName)}" target="_blank" class="sod-btn-sm" style="text-decoration:none;" title="Open in standard Desk">Desk ↗</a>
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
      self.$content
        .find("#sod-report-desc-text")
        .text($opt.data("desc") || "Official ERPNext report");
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
        if (r.message) {
          self.activeReportData = r.message;
          self.renderLiveReportTable(r.message);
        }
      },
      error: (err) => {
        self.$content.find("#sod-report-table-area").html(`
          <div class="sod-empty" style="color:#e03131;">
            Failed to run report: ${frappe.utils.escape_html(err.message || "Execution Error")}
          </div>
        `);
      },
    });
  }

  renderLiveReportTable(reportData) {
    const columns = reportData.columns || [];
    const rawResult = reportData.result || [];
    const summary = reportData.report_summary || [];
    const execTime = reportData.execution_time
      ? `${reportData.execution_time.toFixed(2)}s`
      : "";

    // 1. Render Summary Bar
    const $summaryContainer = this.$content.find(
      "#sod-report-summary-container",
    );
    $summaryContainer.empty();
    if (summary.length) {
      summary.forEach((kpi) => {
        const numVal =
          typeof flt !== "undefined" ? flt(kpi.value) : Number(kpi.value) || 0;
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
          valFormatted = String(
            kpi.value !== null && kpi.value !== undefined ? kpi.value : "",
          );
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
      tableHtml += `<tr><td colspan="${columns.length || 1}" style="text-align:center; padding: 24px; color:#8899aa;">No records returned for current company and date filters.</td></tr>`;
    } else {
      rows.forEach((r) => {
        tableHtml += "<tr>";
        r.forEach((cell, ci) => {
          const colDef = columns[ci] || {};
          let val = cell !== null && cell !== undefined ? cell : "";
          let formatted = val;

          if (colDef.fieldtype === "Currency" && typeof val === "number") {
            const numVal =
              typeof flt !== "undefined" ? flt(val) : Number(val) || 0;
            formatted =
              "₹" +
              numVal.toLocaleString("en-IN", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              });
          } else if (colDef.fieldtype === "Date" && val) {
            formatted = String(val);
          } else if (colDef.fieldtype === "Link" && val && colDef.options) {
            const dtSlug = (colDef.options + "")
              .toLowerCase()
              .replace(/ /g, "-");
            formatted = `<a href="/app/${dtSlug}/${encodeURIComponent(val)}" target="_blank" class="sod-link">${frappe.utils.escape_html(String(val))}</a>`;
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
    this.$content
      .find("#sod-report-row-count")
      .text(`Total Rows: ${rows.length}`);
    this.$content
      .find("#sod-report-exec-time")
      .text(execTime ? `Executed in ${execTime}` : "");
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
        q
          ? `Showing ${matched} matching rows`
          : `Total Rows: ${this.activeReportRows?.length || 0}`,
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
      (c) => `"${(c.label || c.fieldname).replace(/"/g, '""')}"`,
    );
    const csvRows = [cols.join(",")];

    (this.activeReportRows || []).forEach((row) => {
      const escapedRow = row.map((cell) => {
        const strVal = cell !== null && cell !== undefined ? cell + "" : "";
        return `"${strVal.replace(/"/g, '""')}"`;
      });
      csvRows.push(escapedRow.join(","));
    });

    const csvContent =
      "data:text/csv;charset=utf-8," + encodeURIComponent(csvRows.join("\n"));
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", csvContent);
    downloadAnchor.setAttribute(
      "download",
      `${this.currentReportName.toLowerCase().replace(/ /g, "_")}_${frappe.datetime.now_date()}.csv`,
    );
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();

    frappe.show_alert({
      message: "CSV exported successfully",
      indicator: "green",
    });
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
          <div class="sod-card ${color}" data-action="open-desk" data-route="${frappe.utils.escape_html(route || "")}" role="button" tabindex="0" title="Click to view in Desk">
            <div class="sod-label">${frappe.utils.escape_html(label)}</div>
            <strong class="sod-kpi-val">${frappe.utils.escape_html(value)}</strong>
            <small>${frappe.utils.escape_html(desc || "Open ERPNext list ↗")}</small>
            <span class="sod-card-arrow">↗</span>
          </div>
        `;
      });
      html += "</div>";
    }

    // 2. Desk Shortcuts Bar
    if (data.shortcuts && data.shortcuts.length) {
      html += `
        <div class="sod-shortcuts-bar">
          <div class="sod-shortcuts-label">
            <span class="sod-shortcuts-tag">QUICK DESK ACTIONS</span>
            <small style="color:#7583a0; font-size:11px;">Direct ERPNext Desk navigation and record creation</small>
          </div>
          <div class="sod-shortcuts-pills">
      `;
      data.shortcuts.forEach((sc) => {
        html += `
          <a href="${frappe.utils.escape_html(sc.route)}" target="_blank" class="sod-shortcut-pill" title="Open ${frappe.utils.escape_html(sc.label)} in Desk">
            <span class="sod-sc-icon">${sc.icon || "↗"}</span>
            <span class="sod-sc-text">${frappe.utils.escape_html(sc.label)}</span>
            <span class="sod-sc-arrow">↗</span>
          </a>
        `;
      });
      html += `
          </div>
        </div>
      `;
    }

    // 3. Interactive Charts on Specific Pages
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

    // 4. Project Detail Pipeline (Page 2)
    if (pageKey === "project_detail" && data.pipeline) {
      html += `
        <section class="sod-panel">
          <h2>${frappe.utils.escape_html(data.pipeline.project_name)} · <a href="/app/project/${encodeURIComponent(data.pipeline.project)}" target="_blank" class="sod-link">${frappe.utils.escape_html(data.pipeline.project)}</a></h2>
          <p>Customer: <b>${frappe.utils.escape_html(data.pipeline.customer)}</b> · Milestone: <b>${data.pipeline.percent_complete}%</b> · Output: <b>${data.pipeline.manufacturing_progress}%</b></p>
          ${this.renderPipelineMarkup(data.pipeline)}
        </section>
      `;

      if (data.project_fields) {
        const pf = data.project_fields;
        html += `
          <div class="sod-grid sod-two" style="margin-top: 17px;">
            <div class="sod-panel">
              <div class="sod-panel-head">
                <div>
                  <h2>Project Financial Margins</h2>
                  <p>Budget vs actual costs and billing realization</p>
                </div>
                <div>
                  <a href="/app/project/${encodeURIComponent(pf.name || "")}" target="_blank" class="sod-btn-sm">Open Project ↗</a>
                </div>
              </div>
              <div class="sod-feed"><b>Estimated Budget:</b> <span>${pf.estimated_cost}</span></div>
              <div class="sod-feed"><b>Actual Cost Incurred:</b> <span>${pf.actual_cost}</span></div>
              <div class="sod-feed"><b>Cost Variance:</b> <span>${pf.cost_variance}</span></div>
              <div class="sod-feed"><b>Total Billed:</b> <span>${pf.total_billed}</span></div>
              <div class="sod-feed"><b>Net Margin:</b> <span style="color:#12b886; font-weight:700;">${pf.margin}</span></div>
            </div>
            <div class="sod-panel">
              <h2>Milestone Tasks & Deadlines</h2>
              <p>Critical path deliverables</p>
              <div class="sod-tablewrap">
                <table class="sod-table">
                  <thead><tr><th>TASK</th><th>STATUS</th><th>DUE DATE</th></tr></thead>
                  <tbody>
        `;
        (data.tasks || []).forEach((t) => {
          html += `<tr><td><a href="/app/task/${encodeURIComponent(t.task_id || t.task)}" target="_blank" class="sod-link">${frappe.utils.escape_html(t.task)}</a></td><td><span class="sod-pill ${t.status === "Completed" ? "green" : "blue"}">${t.status}</span></td><td>${frappe.utils.escape_html(t.date || "—")}</td></tr>`;
        });
        html += `
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        `;
      }
    }

    // 5. Data Tables with Linked Records
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
            const strCell = String(
              cell !== null && cell !== undefined ? cell : "",
            );

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
              html += `<td><a href="/app/project/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "projects" && ci === 1) {
              const projId = r[0];
              html += `<td><a href="javascript:void(0)" data-project-drill="${encodeURIComponent(projId)}" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (
              pageKey === "projects" &&
              ci === 2 &&
              strCell !== "Unassigned"
            ) {
              html += `<td><a href="/app/customer/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "projects" && ci === 3 && strCell !== "—") {
              html += `<td><a href="/app/sales-order/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "customers" && (ci === 0 || ci === 1)) {
              const custId = r[0];
              html += `<td><a href="/app/customer/${encodeURIComponent(custId)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "sales_orders" && ci === 0) {
              html += `<td><a href="/app/sales-order/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "sales_orders" && ci === 1) {
              html += `<td><a href="/app/customer/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "manufacturing" && ci === 0) {
              html += `<td><a href="/app/work-order/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "stock_quality" && (ci === 0 || ci === 1)) {
              const whId = r[0];
              html += `<td><a href="/app/warehouse/${encodeURIComponent(whId)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (
              (pageKey === "invoicing" || pageKey === "finance") &&
              ci === 0
            ) {
              const isPurchase =
                strCell.toUpperCase().startsWith("PINV") ||
                strCell.toUpperCase().startsWith("PUR-");
              const dt = isPurchase ? "purchase-invoice" : "sales-invoice";
              html += `<td><a href="/app/${dt}/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (
              (pageKey === "invoicing" || pageKey === "finance") &&
              ci === 1
            ) {
              html += `<td><a href="/app/customer/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "payments" && ci === 0) {
              html += `<td><a href="/app/payment-entry/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "taxes" && ci === 0) {
              html += `<td><a href="/app/sales-taxes-and-charges-template/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "banking" && ci === 0) {
              html += `<td><a href="/app/bank-account/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "budget" && ci === 0) {
              html += `<td><a href="/app/budget/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "share_management" && ci === 0) {
              html += `<td><a href="/app/shareholder/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (pageKey === "subscription" && ci === 0) {
              html += `<td><a href="/app/subscription/${encodeURIComponent(strCell)}" target="_blank" class="sod-link">${frappe.utils.escape_html(strCell)}</a></td>`;
            } else if (
              strCell === "Delayed" ||
              strCell === "Stop" ||
              strCell === "Disabled" ||
              strCell.startsWith("Critical")
            ) {
              html += `<td><span class="sod-pill red">${frappe.utils.escape_html(strCell)}</span></td>`;
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
              html += `<td><span class="sod-pill red">${frappe.utils.escape_html(strCell)}</span></td>`;
            } else if (
              strCell.startsWith("Overdue 1-30d") ||
              strCell === "Optional" ||
              strCell === "Warn"
            ) {
              html += `<td><span class="sod-pill amber">${frappe.utils.escape_html(strCell)}</span></td>`;
            } else if (
              strCell === "Current (Not Due)" ||
              strCell === "Open" ||
              strCell === "Draft" ||
              strCell === "Receive" ||
              strCell === "Pay"
            ) {
              html += `<td><span class="sod-pill blue">${frappe.utils.escape_html(strCell)}</span></td>`;
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
     PIPELINE MARKUP & MODAL
  ------------------------------------------------------------- */
  renderPipelineMarkup(p) {
    const stages = p.stages || [];
    let html = '<div class="sod-pipeline">';

    stages.forEach((st, i) => {
      html += `
        <div class="sod-stage ${st.status}" role="button" tabindex="0" data-project="${frappe.utils.escape_html(p.project)}" data-stage-id="${st.id}">
          <div class="sod-circle">${st.icon}</div>
          <strong>${frappe.utils.escape_html(st.label)}</strong>
          <small>${frappe.utils.escape_html(st.info)}</small>
          <em>${frappe.utils.escape_html(st.badge)}</em>
        </div>
      `;
      if (i < stages.length - 1) {
        html += '<div class="sod-connector"></div>';
      }
    });

    html += "</div>";
    return html;
  }

  bindPipelineClicks() {
    const self = this;
    this.$content.find(".sod-stage").on("click", function () {
      const project = $(this).data("project");
      const stageId = $(this).data("stage-id");
      self.showStageModal(project, stageId);
    });
  }

  showStageModal(projectName, stageId) {
    const pipelineData =
      (this.activeData?.pipelines || []).find(
        (p) => p.project === projectName,
      ) || this.activeData?.pipeline;
    if (!pipelineData) return;

    const stage = (pipelineData.stages || []).find((s) => s.id === stageId);
    if (!stage) return;

    this.$modalTitle.text(`${stage.label} · ${pipelineData.project_name}`);

    let recordsHtml = "";
    if (stage.records && stage.records.length) {
      recordsHtml = stage.records
        .map(
          (rec) =>
            `<li><a href="/app/${encodeURIComponent(stage.doctype.toLowerCase().replace(/ /g, "-"))}/${encodeURIComponent(rec)}" target="_blank" class="sod-link" style="font-size:12.5px;">${frappe.utils.escape_html(rec)} ↗</a></li>`,
        )
        .join("");
    } else {
      recordsHtml = `<li><em>No ${stage.doctype} records recorded (${stage.badge}).</em></li>`;
    }

    this.$modalBody.html(`
      <p><b>DocType:</b> ${stage.doctype} &nbsp;|&nbsp; <b>Customer:</b> ${frappe.utils.escape_html(pipelineData.customer)}</p>
      <div class="sod-modal-box">
        <b>Stage Status:</b> <span class="sod-pill ${stage.status === "done" ? "green" : stage.status === "current" ? "purple" : "blue"}">${stage.status.toUpperCase()}</span><br>
        <b>Summary:</b> ${frappe.utils.escape_html(stage.badge)}<br>
        <b>Description:</b> ${frappe.utils.escape_html(stage.info)}<br>
        <b>Linked Records (${stage.count}):</b>
        <ul style="margin: 8px 0 0 16px; padding: 0;">${recordsHtml}</ul>
      </div>
      <p style="font-size: 11.5px; color: #7788a0;">Clicking any record opens the native ERPNext document in Desk.</p>
    `);

    this.$modalFoot.html(`
      <a class="sod-btn-primary" href="/app/${encodeURIComponent(stage.doctype.toLowerCase().replace(/ /g, "-"))}?project=${encodeURIComponent(projectName)}" target="_blank">
        View All ${stage.doctype}s ↗
      </a>
    `);

    this.$modal.addClass("show");
  }

  show() {
    document.documentElement.classList.add("sod-page-active");
    document.body.classList.add("sod-page-active");
    $(".main-section").scrollTop(0);
    window.scrollTo(0, 0);

    // Purge any rogue duplicate wrappers or footers
    if (this.root) {
      $(".sod-wrapper").not(this.root).remove();
      $(".sod-footer").remove();
      $(".sod-wrapper ~ .sod-wrapper").remove();
    }

    this.refreshCurrentPage();
    if (!this.refreshTimer) {
      // 15-second background sync interval
      this.refreshTimer = setInterval(() => {
        this.smoothRefresh();
      }, 15000);
    }
  }

  hide() {
    document.documentElement.classList.remove("sod-page-active");
    document.body.classList.remove("sod-page-active");
    if (this.refreshTimer) {
      clearInterval(this.refreshTimer);
      this.refreshTimer = null;
    }
  }
};
